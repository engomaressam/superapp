<![CDATA["""
Base Agent Class
All specialized agents inherit from this base.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import structlog

logger = structlog.get_logger()


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Tool:
    """
    A tool that an agent can use to perform actions.
    """
    name: str
    description: str
    parameters: Dict[str, Any]
    function: callable
    requires_confirmation: bool = False
    estimated_cost: Optional[float] = None
    timeout_seconds: int = 60


@dataclass
class Task:
    """
    A task to be executed by an agent.
    """
    id: str
    type: str
    agent: str
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentResult:
    """
    Result of an agent execution.
    """
    success: bool
    task_id: str
    agent: str
    data: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    type: Optional[str] = None
    requires_confirmation: bool = False
    execution_time_ms: float = 0
    tools_used: List[str] = field(default_factory=list)
    cost_incurred: float = 0.0


class BaseAgent(ABC):
    """
    Abstract base class for all ARIA agents.
    
    Each agent specializes in a specific domain and has access
    to domain-specific tools.
    """
    
    # Class attributes to be overridden by subclasses
    name: str = "BaseAgent"
    description: str = "Base agent class"
    
    def __init__(self):
        self.status = AgentStatus.IDLE
        self.tools: List[Tool] = []
        self._initialize_tools()
        
        logger.info(
            "Agent initialized",
            agent=self.name,
            tools=[t.name for t in self.tools]
        )
    
    @abstractmethod
    def _initialize_tools(self) -> None:
        """Initialize domain-specific tools. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def can_handle(self, task: Task) -> bool:
        """
        Check if this agent can handle the given task.
        
        Args:
            task: The task to check
            
        Returns:
            True if agent can handle, False otherwise
        """
        pass
    
    @abstractmethod
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create an execution plan for the task.
        
        Args:
            task: The task to plan
            context: Execution context
            
        Returns:
            List of tool calls to execute
        """
        pass
    
    async def execute(
        self,
        task: Dict[str, Any],
        state: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute a task and return the result.
        
        Args:
            task: Task definition
            state: Current workflow state
            
        Returns:
            AgentResult with execution outcome
        """
        import time
        start_time = time.time()
        tools_used = []
        
        task_obj = Task(
            id=task.get("id", "unknown"),
            type=task.get("type", "unknown"),
            agent=self.name,
            parameters=task.get("parameters", {})
        )
        
        try:
            self.status = AgentStatus.PLANNING
            
            logger.info(
                "Agent planning task",
                agent=self.name,
                task_id=task_obj.id,
                task_type=task_obj.type
            )
            
            # Create execution plan
            plan = await self.plan(task_obj, state)
            
            if not plan:
                return AgentResult(
                    success=True,
                    task_id=task_obj.id,
                    agent=self.name,
                    data={"message": "No actions required"},
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            self.status = AgentStatus.EXECUTING
            
            # Execute each step in the plan
            results = []
            requires_confirmation = False
            
            for step in plan:
                tool = self._get_tool(step.get("tool"))
                
                if not tool:
                    raise ValueError(f"Unknown tool: {step.get('tool')}")
                
                # Check if confirmation is needed
                if tool.requires_confirmation:
                    requires_confirmation = True
                    results.append({
                        "tool": tool.name,
                        "status": "pending_confirmation",
                        "parameters": step.get("parameters", {})
                    })
                    continue
                
                # Execute tool with timeout
                try:
                    result = await asyncio.wait_for(
                        tool.function(**step.get("parameters", {})),
                        timeout=tool.timeout_seconds
                    )
                    results.append({
                        "tool": tool.name,
                        "status": "success",
                        "result": result
                    })
                    tools_used.append(tool.name)
                    
                except asyncio.TimeoutError:
                    logger.warning(
                        "Tool execution timed out",
                        tool=tool.name,
                        timeout=tool.timeout_seconds
                    )
                    results.append({
                        "tool": tool.name,
                        "status": "timeout",
                        "error": f"Execution timed out after {tool.timeout_seconds}s"
                    })
            
            self.status = AgentStatus.COMPLETED
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(
                "Agent completed task",
                agent=self.name,
                task_id=task_obj.id,
                execution_time_ms=execution_time,
                tools_used=tools_used
            )
            
            return AgentResult(
                success=True,
                task_id=task_obj.id,
                agent=self.name,
                data=self._aggregate_results(results),
                action=self._extract_action(results),
                type=task_obj.type,
                requires_confirmation=requires_confirmation,
                execution_time_ms=execution_time,
                tools_used=tools_used
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            
            logger.error(
                "Agent task failed",
                agent=self.name,
                task_id=task_obj.id,
                error=str(e)
            )
            
            return AgentResult(
                success=False,
                task_id=task_obj.id,
                agent=self.name,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
                tools_used=tools_used
            )
    
    def _get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
    
    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from multiple tool calls."""
        return {
            "steps": results,
            "summary": self._create_summary(results)
        }
    
    def _extract_action(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract actionable result from tool executions."""
        for result in results:
            if result.get("status") == "success" and result.get("result"):
                return result.get("result")
        return None
    
    def _create_summary(self, results: List[Dict[str, Any]]) -> str:
        """Create a human-readable summary of results."""
        successful = sum(1 for r in results if r.get("status") == "success")
        total = len(results)
        return f"Completed {successful}/{total} steps"


class RetryableMixin:
    """
    Mixin that adds retry capability to agents.
    """
    
    async def execute_with_retry(
        self,
        task: Task,
        context: Dict[str, Any],
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> AgentResult:
        """
        Execute with exponential backoff retry.
        """
        last_error = None
        
        for attempt in range(max_retries):
            result = await self.execute(task.__dict__, context)
            
            if result.success:
                return result
            
            # Check if error is retryable
            if not self._is_retryable(result.error):
                return result
            
            last_error = result.error
            
            # Exponential backoff
            wait_time = backoff_factor ** attempt
            logger.info(
                "Retrying after failure",
                agent=self.name,
                attempt=attempt + 1,
                wait_time=wait_time
            )
            await asyncio.sleep(wait_time)
        
        return AgentResult(
            success=False,
            task_id=task.id,
            agent=self.name,
            error=f"Max retries exceeded. Last error: {last_error}"
        )
    
    def _is_retryable(self, error: str) -> bool:
        """Determine if an error is worth retrying."""
        if not error:
            return False
            
        retryable_patterns = [
            "timeout",
            "rate limit",
            "connection",
            "temporary",
            "503",
            "502",
            "504",
            "network"
        ]
        
        error_lower = error.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)
]]>
