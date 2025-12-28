<![CDATA[# 🤖 Agent Design Patterns

## Overview

This document details the design patterns and implementation strategies for ARIA's multi-agent system.

---

## Agent Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT LIFECYCLE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. INITIALIZATION                                              │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────┐                                                │
│  │ Load Config │ ─── API keys, endpoints, constraints           │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │ Init Tools  │ ─── Connect to external services               │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  2. TASK RECEPTION                                              │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────┐                                                │
│  │ Validate    │ ─── Check if agent can handle task             │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  3. EXECUTION                                                   │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────┐                                                │
│  │ Plan Steps  │ ─── Break task into tool calls                 │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │ Execute     │ ─── Run tools, handle errors                   │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  4. RESULT REPORTING                                            │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────┐                                                │
│  │ Format      │ ─── Structure results for aggregator           │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │ Cleanup     │ ─── Release resources, log metrics             │
│  └─────────────┘                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Base Agent Implementation

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    function: callable
    requires_confirmation: bool = False
    cost_estimate: Optional[float] = None

@dataclass
class Task:
    id: str
    type: str
    parameters: dict
    priority: int = 1
    dependencies: List[str] = None
    timeout: int = 300  # seconds
    max_retries: int = 3

@dataclass
class AgentResult:
    success: bool
    data: Optional[dict]
    error: Optional[str]
    execution_time: float
    tools_used: List[str]
    cost_incurred: float = 0.0

class BaseAgent(ABC):
    """
    Abstract base class for all ARIA agents.
    
    Each agent specializes in a specific domain (transport, calendar, etc.)
    and has access to a set of tools for executing tasks in that domain.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.name = self.__class__.__name__
        self.status = AgentStatus.IDLE
        self.tools: List[Tool] = []
        self._initialize_tools()
    
    @abstractmethod
    def _initialize_tools(self) -> None:
        """Initialize domain-specific tools."""
        pass
    
    @abstractmethod
    async def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the given task."""
        pass
    
    @abstractmethod
    async def plan(self, task: Task, context: dict) -> List[dict]:
        """
        Create an execution plan for the task.
        Returns a list of tool calls to be executed.
        """
        pass
    
    async def execute(self, task: Task, context: dict) -> AgentResult:
        """
        Execute a task and return the result.
        """
        import time
        start_time = time.time()
        tools_used = []
        
        try:
            self.status = AgentStatus.PLANNING
            
            # Create execution plan
            plan = await self.plan(task, context)
            
            self.status = AgentStatus.EXECUTING
            
            # Execute each step in the plan
            results = []
            for step in plan:
                tool = self._get_tool(step["tool"])
                if not tool:
                    raise ValueError(f"Unknown tool: {step['tool']}")
                
                # Check if confirmation needed
                if tool.requires_confirmation:
                    self.status = AgentStatus.WAITING_CONFIRMATION
                    confirmation = await self._request_confirmation(tool, step)
                    if not confirmation:
                        return AgentResult(
                            success=False,
                            data=None,
                            error="User declined action",
                            execution_time=time.time() - start_time,
                            tools_used=tools_used
                        )
                    self.status = AgentStatus.EXECUTING
                
                # Execute tool
                result = await tool.function(**step.get("parameters", {}))
                results.append(result)
                tools_used.append(tool.name)
            
            self.status = AgentStatus.COMPLETED
            
            return AgentResult(
                success=True,
                data=self._aggregate_results(results),
                error=None,
                execution_time=time.time() - start_time,
                tools_used=tools_used
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return AgentResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=time.time() - start_time,
                tools_used=tools_used
            )
    
    def _get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
    
    async def _request_confirmation(self, tool: Tool, step: dict) -> bool:
        """Request user confirmation for a sensitive action."""
        # This would integrate with the frontend
        # For now, returns True in demo mode
        return True
    
    def _aggregate_results(self, results: List[Any]) -> dict:
        """Combine results from multiple tool calls."""
        return {"results": results}
```

---

## Specialized Agent Implementations

### Calendar Agent

```python
class CalendarAgent(BaseAgent):
    """
    Manages calendar operations: checking availability,
    creating events, finding conflicts.
    """
    
    def _initialize_tools(self):
        self.tools = [
            Tool(
                name="get_events",
                description="Get calendar events for a date range",
                parameters={
                    "start_date": "datetime",
                    "end_date": "datetime",
                    "calendar_id": "string (optional)"
                },
                function=self._get_events
            ),
            Tool(
                name="create_event",
                description="Create a new calendar event",
                parameters={
                    "title": "string",
                    "start_time": "datetime",
                    "end_time": "datetime",
                    "location": "string (optional)",
                    "description": "string (optional)"
                },
                function=self._create_event,
                requires_confirmation=True
            ),
            Tool(
                name="check_conflicts",
                description="Check for scheduling conflicts",
                parameters={
                    "proposed_time": "datetime",
                    "duration_minutes": "int"
                },
                function=self._check_conflicts
            ),
            Tool(
                name="find_free_slots",
                description="Find available time slots",
                parameters={
                    "date": "date",
                    "duration_minutes": "int",
                    "preferred_time": "string (morning/afternoon/evening)"
                },
                function=self._find_free_slots
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        calendar_tasks = [
            "check_availability",
            "create_event",
            "find_free_time",
            "check_conflicts",
            "get_schedule"
        ]
        return task.type in calendar_tasks
    
    async def plan(self, task: Task, context: dict) -> List[dict]:
        if task.type == "check_availability":
            return [{
                "tool": "get_events",
                "parameters": {
                    "start_date": task.parameters.get("date"),
                    "end_date": task.parameters.get("date")
                }
            }]
        
        elif task.type == "create_event":
            # First check for conflicts, then create
            return [
                {
                    "tool": "check_conflicts",
                    "parameters": {
                        "proposed_time": task.parameters.get("start_time"),
                        "duration_minutes": task.parameters.get("duration", 60)
                    }
                },
                {
                    "tool": "create_event",
                    "parameters": task.parameters
                }
            ]
        
        elif task.type == "find_free_time":
            return [{
                "tool": "find_free_slots",
                "parameters": {
                    "date": task.parameters.get("date"),
                    "duration_minutes": task.parameters.get("duration", 60),
                    "preferred_time": task.parameters.get("preferred_time", "afternoon")
                }
            }]
        
        return []
    
    async def _get_events(self, start_date, end_date, calendar_id=None):
        """Fetch events from Google Calendar API."""
        # Implementation using Google Calendar API
        pass
    
    async def _create_event(self, title, start_time, end_time, location=None, description=None):
        """Create event via Google Calendar API."""
        pass
    
    async def _check_conflicts(self, proposed_time, duration_minutes):
        """Check if proposed time conflicts with existing events."""
        pass
    
    async def _find_free_slots(self, date, duration_minutes, preferred_time):
        """Find available time slots on given date."""
        pass
```

### Transport Agent

```python
class TransportAgent(BaseAgent):
    """
    Handles transportation requests: ride booking,
    price estimation, tracking.
    """
    
    def _initialize_tools(self):
        self.tools = [
            Tool(
                name="get_ride_estimate",
                description="Get price and time estimate for a ride",
                parameters={
                    "pickup": "Location",
                    "dropoff": "Location",
                    "ride_type": "string (UberX, UberXL, etc.)"
                },
                function=self._get_estimate
            ),
            Tool(
                name="book_ride",
                description="Book a ride",
                parameters={
                    "pickup": "Location",
                    "dropoff": "Location",
                    "ride_type": "string",
                    "scheduled_time": "datetime (optional)"
                },
                function=self._book_ride,
                requires_confirmation=True,
                cost_estimate=15.0  # Average ride cost
            ),
            Tool(
                name="get_ride_status",
                description="Get status of an active ride",
                parameters={
                    "ride_id": "string"
                },
                function=self._get_status
            ),
            Tool(
                name="cancel_ride",
                description="Cancel a booked ride",
                parameters={
                    "ride_id": "string"
                },
                function=self._cancel_ride,
                requires_confirmation=True
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        transport_tasks = [
            "book_ride",
            "get_ride_estimate",
            "track_ride",
            "cancel_ride",
            "schedule_pickup"
        ]
        return task.type in transport_tasks
    
    async def plan(self, task: Task, context: dict) -> List[dict]:
        if task.type == "book_ride":
            # Get estimate first, then book
            return [
                {
                    "tool": "get_ride_estimate",
                    "parameters": {
                        "pickup": task.parameters.get("pickup"),
                        "dropoff": task.parameters.get("dropoff"),
                        "ride_type": task.parameters.get("ride_type", "UberX")
                    }
                },
                {
                    "tool": "book_ride",
                    "parameters": task.parameters
                }
            ]
        
        elif task.type == "get_ride_estimate":
            return [{
                "tool": "get_ride_estimate",
                "parameters": task.parameters
            }]
        
        return []
    
    async def _get_estimate(self, pickup, dropoff, ride_type):
        """Get ride estimate from Uber API."""
        pass
    
    async def _book_ride(self, pickup, dropoff, ride_type, scheduled_time=None):
        """Book ride via Uber API."""
        pass
    
    async def _get_status(self, ride_id):
        """Get ride status."""
        pass
    
    async def _cancel_ride(self, ride_id):
        """Cancel ride."""
        pass
```

### Medical Agent

```python
class MedicalAgent(BaseAgent):
    """
    Handles healthcare-related tasks using web automation
    for platforms like Vezeeta.
    """
    
    def _initialize_tools(self):
        self.tools = [
            Tool(
                name="search_doctors",
                description="Search for doctors by specialty and location",
                parameters={
                    "specialty": "string",
                    "location": "string",
                    "insurance": "string (optional)"
                },
                function=self._search_doctors
            ),
            Tool(
                name="get_available_slots",
                description="Get available appointment slots for a doctor",
                parameters={
                    "doctor_id": "string",
                    "date": "date"
                },
                function=self._get_slots
            ),
            Tool(
                name="book_appointment",
                description="Book a medical appointment",
                parameters={
                    "doctor_id": "string",
                    "slot_id": "string",
                    "patient_info": "dict"
                },
                function=self._book_appointment,
                requires_confirmation=True,
                cost_estimate=50.0  # Average consultation fee
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        medical_tasks = [
            "find_doctor",
            "book_appointment",
            "check_availability",
            "cancel_appointment"
        ]
        return task.type in medical_tasks
    
    async def plan(self, task: Task, context: dict) -> List[dict]:
        if task.type == "book_appointment":
            # Full flow: search -> get slots -> book
            return [
                {
                    "tool": "search_doctors",
                    "parameters": {
                        "specialty": task.parameters.get("specialty"),
                        "location": task.parameters.get("location")
                    }
                },
                {
                    "tool": "get_available_slots",
                    "parameters": {
                        "doctor_id": "{result.doctors[0].id}",  # Templated
                        "date": task.parameters.get("preferred_date")
                    }
                },
                {
                    "tool": "book_appointment",
                    "parameters": {
                        "doctor_id": "{result.doctors[0].id}",
                        "slot_id": "{result.slots[0].id}",
                        "patient_info": context.get("user_info")
                    }
                }
            ]
        
        return []
    
    async def _search_doctors(self, specialty, location, insurance=None):
        """Search doctors using Vezeeta web automation."""
        from ..automation.vezeeta import VezeetaAutomation
        
        automation = VezeetaAutomation()
        return await automation.search_doctors(specialty, location, insurance)
    
    async def _get_slots(self, doctor_id, date):
        """Get available slots via web automation."""
        pass
    
    async def _book_appointment(self, doctor_id, slot_id, patient_info):
        """Book appointment via web automation."""
        pass
```

---

## Agent Communication Patterns

### Request-Response Pattern

```python
@dataclass
class AgentRequest:
    request_id: str
    task: Task
    context: dict
    sender: str
    timestamp: datetime
    timeout: int = 300

@dataclass
class AgentResponse:
    request_id: str
    result: AgentResult
    responder: str
    timestamp: datetime

class AgentBus:
    """
    Message bus for agent communication.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
    
    def register(self, agent: BaseAgent):
        self.agents[agent.name] = agent
    
    async def send_request(
        self,
        target_agent: str,
        task: Task,
        context: dict,
        sender: str = "orchestrator"
    ) -> AgentResult:
        """Send a request to an agent and wait for response."""
        
        request_id = str(uuid.uuid4())
        request = AgentRequest(
            request_id=request_id,
            task=task,
            context=context,
            sender=sender,
            timestamp=datetime.now()
        )
        
        # Get target agent
        agent = self.agents.get(target_agent)
        if not agent:
            raise ValueError(f"Unknown agent: {target_agent}")
        
        # Execute and return result
        result = await agent.execute(task, context)
        
        return result
    
    async def broadcast(
        self,
        task: Task,
        context: dict
    ) -> Dict[str, AgentResult]:
        """
        Broadcast a task to all agents that can handle it.
        Returns results from all responding agents.
        """
        results = {}
        
        # Find capable agents
        capable_agents = []
        for name, agent in self.agents.items():
            if await agent.can_handle(task):
                capable_agents.append(name)
        
        # Execute in parallel
        tasks = [
            self.send_request(agent_name, task, context)
            for agent_name in capable_agents
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for agent_name, response in zip(capable_agents, responses):
            if isinstance(response, Exception):
                results[agent_name] = AgentResult(
                    success=False,
                    data=None,
                    error=str(response),
                    execution_time=0,
                    tools_used=[]
                )
            else:
                results[agent_name] = response
        
        return results
```

### Supervisor Pattern

```python
class SupervisorAgent(BaseAgent):
    """
    A supervisor agent that coordinates multiple child agents.
    """
    
    def __init__(self, config: dict, child_agents: List[BaseAgent]):
        super().__init__(config)
        self.children = {agent.name: agent for agent in child_agents}
        self.bus = AgentBus()
        
        for agent in child_agents:
            self.bus.register(agent)
    
    async def execute(self, task: Task, context: dict) -> AgentResult:
        """
        Decompose task and delegate to child agents.
        """
        # Decompose the complex task
        subtasks = await self._decompose_task(task)
        
        # Determine dependencies and execution order
        execution_plan = self._create_execution_plan(subtasks)
        
        # Execute plan
        results = {}
        for batch in execution_plan:
            # Execute independent tasks in parallel
            batch_results = await asyncio.gather(*[
                self._execute_subtask(subtask, context, results)
                for subtask in batch
            ])
            
            for subtask, result in zip(batch, batch_results):
                results[subtask.id] = result
        
        # Aggregate results
        return self._aggregate_child_results(results)
    
    async def _decompose_task(self, task: Task) -> List[Task]:
        """Use LLM to decompose complex task into subtasks."""
        pass
    
    def _create_execution_plan(self, subtasks: List[Task]) -> List[List[Task]]:
        """
        Create execution batches based on dependencies.
        Tasks without dependencies are in the first batch.
        """
        pass
    
    async def _execute_subtask(
        self,
        subtask: Task,
        context: dict,
        previous_results: dict
    ) -> AgentResult:
        """Execute a subtask, injecting previous results into context."""
        pass
```

---

## Error Handling & Recovery

```python
class AgentErrorHandler:
    """
    Handles errors during agent execution.
    """
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(
        self,
        agent: BaseAgent,
        task: Task,
        context: dict
    ) -> AgentResult:
        """Execute agent task with automatic retry on failure."""
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = await agent.execute(task, context)
                
                if result.success:
                    return result
                
                # Check if error is retryable
                if not self._is_retryable(result.error):
                    return result
                
                last_error = result.error
                
            except Exception as e:
                last_error = str(e)
                
                if not self._is_retryable(str(e)):
                    raise
            
            # Exponential backoff
            wait_time = self.backoff_factor ** attempt
            await asyncio.sleep(wait_time)
        
        return AgentResult(
            success=False,
            data=None,
            error=f"Max retries exceeded. Last error: {last_error}",
            execution_time=0,
            tools_used=[]
        )
    
    def _is_retryable(self, error: str) -> bool:
        """Determine if an error is worth retrying."""
        retryable_patterns = [
            "timeout",
            "rate limit",
            "connection",
            "temporary",
            "503",
            "502",
            "504"
        ]
        
        error_lower = error.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)


class FallbackHandler:
    """
    Handles fallbacks when primary approach fails.
    """
    
    def __init__(self, fallback_chain: List[BaseAgent]):
        self.chain = fallback_chain
    
    async def execute_with_fallback(
        self,
        task: Task,
        context: dict
    ) -> AgentResult:
        """Try each agent in the fallback chain until one succeeds."""
        
        errors = []
        
        for agent in self.chain:
            if not await agent.can_handle(task):
                continue
            
            result = await agent.execute(task, context)
            
            if result.success:
                return result
            
            errors.append(f"{agent.name}: {result.error}")
        
        return AgentResult(
            success=False,
            data=None,
            error=f"All fallbacks failed: {'; '.join(errors)}",
            execution_time=0,
            tools_used=[]
        )
```

---

## Testing Agents

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestCalendarAgent:
    
    @pytest.fixture
    def agent(self):
        config = {"google_calendar_credentials": "test"}
        return CalendarAgent(config)
    
    @pytest.mark.asyncio
    async def test_can_handle_availability_check(self, agent):
        task = Task(
            id="test-1",
            type="check_availability",
            parameters={"date": "2024-01-15"}
        )
        assert await agent.can_handle(task) == True
    
    @pytest.mark.asyncio
    async def test_cannot_handle_ride_booking(self, agent):
        task = Task(
            id="test-2",
            type="book_ride",
            parameters={}
        )
        assert await agent.can_handle(task) == False
    
    @pytest.mark.asyncio
    async def test_plan_creates_correct_steps(self, agent):
        task = Task(
            id="test-3",
            type="create_event",
            parameters={
                "title": "Meeting",
                "start_time": "2024-01-15T10:00:00",
                "duration": 60
            }
        )
        
        plan = await agent.plan(task, {})
        
        assert len(plan) == 2
        assert plan[0]["tool"] == "check_conflicts"
        assert plan[1]["tool"] == "create_event"
    
    @pytest.mark.asyncio
    async def test_execution_success(self, agent):
        task = Task(
            id="test-4",
            type="check_availability",
            parameters={"date": "2024-01-15"}
        )
        
        with patch.object(agent, '_get_events', new_callable=AsyncMock) as mock:
            mock.return_value = [{"title": "Existing Meeting"}]
            
            result = await agent.execute(task, {})
            
            assert result.success == True
            assert "get_events" in result.tools_used
```

---

## Next Steps

- See [Integration Guide](INTEGRATION_GUIDE.md) for connecting to external services
- See [Security Best Practices](SECURITY.md) for secure agent implementation
]]>
