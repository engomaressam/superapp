<![CDATA["""
ARIA Multi-Agent Orchestrator
LangGraph-based workflow management for agent coordination.
"""

from typing import TypedDict, Annotated, Literal, List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import operator
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from app.agents.dispatcher import DispatcherAgent
from app.agents.calendar import CalendarAgent
from app.agents.transport import TransportAgent
from app.agents.medical import MedicalAgent
from app.agents.movie import MovieAgent
from app.agents.reminder import ReminderAgent
from app.config import settings


# State definition for the workflow
class AgentState(TypedDict):
    """
    State that flows through the agent workflow.
    """
    # Input
    user_message: str
    user_id: str
    conversation_id: str
    
    # Context
    location: Optional[Dict[str, float]]
    timezone: str
    
    # Processing
    intent: Optional[Dict[str, Any]]
    plan: Optional[List[Dict[str, Any]]]
    current_agent: Optional[str]
    
    # Results
    agent_results: Annotated[Dict[str, Any], operator.or_]
    
    # Output
    response: Optional[str]
    actions: List[Dict[str, Any]]
    
    # Conversation history
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Error tracking
    errors: List[Dict[str, str]]
    
    # Control
    requires_confirmation: bool
    iteration_count: int


@dataclass
class ExecutionPlan:
    """
    Plan for executing a user request.
    """
    tasks: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    parallel_groups: List[List[str]]


class Orchestrator:
    """
    Main orchestrator that coordinates multiple agents using LangGraph.
    
    The orchestrator:
    1. Receives user input
    2. Dispatches to analyze intent and create execution plan
    3. Routes to appropriate specialized agents
    4. Aggregates results
    5. Generates final response
    """
    
    def __init__(self):
        # Initialize agents
        self.dispatcher = DispatcherAgent()
        self.agents = {
            "calendar": CalendarAgent(),
            "transport": TransportAgent(),
            "medical": MedicalAgent(),
            "movie": MovieAgent(),
            "reminder": ReminderAgent(),
        }
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Flow:
        1. parse_intent -> Understand what user wants
        2. create_plan -> Break into subtasks
        3. route_to_agents -> Execute appropriate agents
        4. aggregate_results -> Combine results
        5. generate_response -> Create user-friendly response
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_intent", self._parse_intent_node)
        workflow.add_node("create_plan", self._create_plan_node)
        workflow.add_node("execute_calendar", self._execute_calendar_node)
        workflow.add_node("execute_transport", self._execute_transport_node)
        workflow.add_node("execute_medical", self._execute_medical_node)
        workflow.add_node("execute_movie", self._execute_movie_node)
        workflow.add_node("execute_reminder", self._execute_reminder_node)
        workflow.add_node("aggregate_results", self._aggregate_results_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("request_confirmation", self._request_confirmation_node)
        
        # Set entry point
        workflow.set_entry_point("parse_intent")
        
        # Add edges
        workflow.add_edge("parse_intent", "create_plan")
        
        # Conditional routing from plan to agents
        workflow.add_conditional_edges(
            "create_plan",
            self._route_to_agents,
            {
                "calendar": "execute_calendar",
                "transport": "execute_transport",
                "medical": "execute_medical",
                "movie": "execute_movie",
                "reminder": "execute_reminder",
                "aggregate": "aggregate_results",
                "direct_response": "generate_response",
            }
        )
        
        # Agent edges - all lead to aggregation or next agent
        for agent_name in ["execute_calendar", "execute_transport", 
                          "execute_medical", "execute_movie", "execute_reminder"]:
            workflow.add_conditional_edges(
                agent_name,
                self._route_after_agent,
                {
                    "next_agent": "create_plan",  # Re-evaluate for next task
                    "aggregate": "aggregate_results",
                    "confirm": "request_confirmation",
                }
            )
        
        # Aggregation and response
        workflow.add_conditional_edges(
            "aggregate_results",
            self._check_confirmation_needed,
            {
                "confirm": "request_confirmation",
                "respond": "generate_response",
            }
        )
        
        workflow.add_edge("request_confirmation", END)
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    async def process(
        self,
        user_message: str,
        user_id: str,
        conversation_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the workflow.
        
        Args:
            user_message: The user's input
            user_id: User identifier
            conversation_id: Conversation identifier
            context: Additional context (location, timezone, etc.)
            
        Returns:
            Dictionary with response and any pending actions
        """
        context = context or {}
        
        # Initialize state
        initial_state: AgentState = {
            "user_message": user_message,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "location": context.get("location"),
            "timezone": context.get("timezone", "UTC"),
            "intent": None,
            "plan": None,
            "current_agent": None,
            "agent_results": {},
            "response": None,
            "actions": [],
            "messages": [HumanMessage(content=user_message)],
            "errors": [],
            "requires_confirmation": False,
            "iteration_count": 0,
        }
        
        # Run the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "response": final_state["response"],
            "actions": final_state["actions"],
            "requires_confirmation": final_state["requires_confirmation"],
            "conversation_id": conversation_id,
        }
    
    async def _parse_intent_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Parse user intent using the dispatcher agent.
        """
        intent = await self.dispatcher.analyze_intent(
            message=state["user_message"],
            context={
                "location": state["location"],
                "timezone": state["timezone"],
            }
        )
        
        return {"intent": intent}
    
    async def _create_plan_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Create execution plan based on intent.
        """
        plan = await self.dispatcher.create_execution_plan(
            intent=state["intent"],
            previous_results=state["agent_results"]
        )
        
        return {"plan": plan}
    
    def _route_to_agents(self, state: AgentState) -> str:
        """
        Route to the appropriate agent based on the plan.
        """
        plan = state.get("plan", [])
        
        if not plan:
            return "direct_response"
        
        # Get the next task to execute
        executed = set(state["agent_results"].keys())
        
        for task in plan:
            task_id = task.get("id")
            agent = task.get("agent")
            
            # Skip already executed tasks
            if task_id in executed:
                continue
            
            # Check dependencies
            dependencies = task.get("dependencies", [])
            if all(dep in executed for dep in dependencies):
                return agent
        
        # All tasks executed
        return "aggregate"
    
    def _route_after_agent(self, state: AgentState) -> str:
        """
        Determine next step after an agent completes.
        """
        current_result = state["agent_results"].get(state["current_agent"], {})
        
        # Check if confirmation is needed
        if current_result.get("requires_confirmation"):
            return "confirm"
        
        # Check if there are more tasks
        plan = state.get("plan", [])
        executed = set(state["agent_results"].keys())
        
        remaining = [t for t in plan if t.get("id") not in executed]
        
        if remaining:
            return "next_agent"
        
        return "aggregate"
    
    def _check_confirmation_needed(self, state: AgentState) -> str:
        """
        Check if any action requires user confirmation.
        """
        for result in state["agent_results"].values():
            if result.get("requires_confirmation"):
                return "confirm"
        
        return "respond"
    
    async def _execute_calendar_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute calendar agent tasks."""
        task = self._get_current_task(state, "calendar")
        result = await self.agents["calendar"].execute(task, state)
        
        return {
            "agent_results": {task["id"]: result},
            "current_agent": "calendar",
        }
    
    async def _execute_transport_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute transport agent tasks."""
        task = self._get_current_task(state, "transport")
        result = await self.agents["transport"].execute(task, state)
        
        return {
            "agent_results": {task["id"]: result},
            "current_agent": "transport",
        }
    
    async def _execute_medical_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute medical agent tasks."""
        task = self._get_current_task(state, "medical")
        result = await self.agents["medical"].execute(task, state)
        
        return {
            "agent_results": {task["id"]: result},
            "current_agent": "medical",
        }
    
    async def _execute_movie_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute movie agent tasks."""
        task = self._get_current_task(state, "movie")
        result = await self.agents["movie"].execute(task, state)
        
        return {
            "agent_results": {task["id"]: result},
            "current_agent": "movie",
        }
    
    async def _execute_reminder_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute reminder agent tasks."""
        task = self._get_current_task(state, "reminder")
        result = await self.agents["reminder"].execute(task, state)
        
        return {
            "agent_results": {task["id"]: result},
            "current_agent": "reminder",
        }
    
    async def _aggregate_results_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Aggregate results from all agents.
        """
        actions = []
        
        for task_id, result in state["agent_results"].items():
            if result.get("action"):
                actions.append({
                    "id": f"action_{task_id}",
                    "type": result.get("type"),
                    "status": "pending_confirmation" if result.get("requires_confirmation") else "ready",
                    "details": result.get("action"),
                })
        
        return {"actions": actions}
    
    async def _generate_response_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Generate a user-friendly response.
        """
        response = await self.dispatcher.generate_response(
            intent=state["intent"],
            results=state["agent_results"],
            actions=state["actions"]
        )
        
        return {"response": response}
    
    async def _request_confirmation_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Prepare confirmation request for user.
        """
        confirmation_prompt = await self.dispatcher.generate_confirmation_request(
            actions=state["actions"],
            results=state["agent_results"]
        )
        
        return {
            "response": confirmation_prompt,
            "requires_confirmation": True,
        }
    
    def _get_current_task(self, state: AgentState, agent: str) -> Dict[str, Any]:
        """Get the next task for a specific agent."""
        for task in state.get("plan", []):
            if task.get("agent") == agent:
                task_id = task.get("id")
                if task_id not in state["agent_results"]:
                    return task
        return {}


# Singleton orchestrator instance
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get or create the orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
]]>
