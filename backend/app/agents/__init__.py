<![CDATA["""
ARIA Agents Module

This module contains all specialized agents for the ARIA system.
"""

from app.agents.base import BaseAgent, Tool, Task, AgentResult, AgentStatus
from app.agents.dispatcher import DispatcherAgent
from app.agents.orchestrator import Orchestrator, get_orchestrator

# Core Agents (from instructors' examples)
from app.agents.transport import TransportAgent
from app.agents.calendar import CalendarAgent
from app.agents.medical import MedicalAgent
from app.agents.movie import MovieAgent
from app.agents.reminder import ReminderAgent

# Extended Agents (additional capabilities)
from app.agents.weather import WeatherAgent
from app.agents.food import FoodAgent
from app.agents.finance import FinanceAgent
from app.agents.shopping import ShoppingAgent
from app.agents.smart_home import SmartHomeAgent
from app.agents.email import EmailAgent
from app.agents.travel import TravelAgent

__all__ = [
    # Base
    "BaseAgent",
    "Tool",
    "Task",
    "AgentResult",
    "AgentStatus",
    "DispatcherAgent",
    "Orchestrator",
    "get_orchestrator",
    # Core Agents
    "TransportAgent",
    "CalendarAgent",
    "MedicalAgent",
    "MovieAgent",
    "ReminderAgent",
    # Extended Agents
    "WeatherAgent",
    "FoodAgent",
    "FinanceAgent",
    "ShoppingAgent",
    "SmartHomeAgent",
    "EmailAgent",
    "TravelAgent",
]
]]>
