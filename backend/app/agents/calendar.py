<![CDATA["""
Calendar Agent
Manages calendar operations and scheduling.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.agents.base import BaseAgent, Tool, Task


@dataclass
class CalendarEvent:
    """Calendar event data."""
    id: str
    title: str
    start: datetime
    end: datetime
    location: Optional[str] = None
    description: Optional[str] = None
    attendees: List[str] = None


class CalendarAgent(BaseAgent):
    """
    Agent specialized in calendar management.
    
    Capabilities:
    - Get events for date ranges
    - Check availability
    - Create new events
    - Find free time slots
    - Check for conflicts
    """
    
    name = "CalendarAgent"
    description = "Manages calendar events and scheduling"
    
    SUPPORTED_TASKS = [
        "check_availability",
        "get_events",
        "create_event",
        "find_free_slots",
        "check_conflicts"
    ]
    
    def _initialize_tools(self):
        """Initialize calendar-specific tools."""
        self.tools = [
            Tool(
                name="get_events",
                description="Get calendar events for a date range",
                parameters={
                    "start_date": "Start of date range",
                    "end_date": "End of date range",
                    "calendar_id": "Optional calendar ID"
                },
                function=self._get_events,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="create_event",
                description="Create a new calendar event",
                parameters={
                    "title": "Event title",
                    "start_time": "Event start time",
                    "end_time": "Event end time",
                    "location": "Optional location",
                    "description": "Optional description"
                },
                function=self._create_event,
                requires_confirmation=True,
                timeout_seconds=30
            ),
            Tool(
                name="check_conflicts",
                description="Check for scheduling conflicts",
                parameters={
                    "proposed_time": "Proposed event time",
                    "duration_minutes": "Event duration"
                },
                function=self._check_conflicts,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="find_free_slots",
                description="Find available time slots",
                parameters={
                    "date": "Date to check",
                    "duration_minutes": "Required duration",
                    "preferred_time": "Preferred time of day"
                },
                function=self._find_free_slots,
                requires_confirmation=False,
                timeout_seconds=30
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the task."""
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution plan for calendar tasks."""
        task_type = task.type
        params = task.parameters
        
        if task_type == "check_availability":
            date = params.get("date", datetime.now().strftime("%Y-%m-%d"))
            return [{
                "tool": "get_events",
                "parameters": {
                    "start_date": date,
                    "end_date": date
                }
            }]
        
        elif task_type == "get_events":
            return [{
                "tool": "get_events",
                "parameters": {
                    "start_date": params.get("start_date"),
                    "end_date": params.get("end_date")
                }
            }]
        
        elif task_type == "create_event":
            # First check for conflicts, then create
            return [
                {
                    "tool": "check_conflicts",
                    "parameters": {
                        "proposed_time": params.get("start_time"),
                        "duration_minutes": params.get("duration", 60)
                    }
                },
                {
                    "tool": "create_event",
                    "parameters": params
                }
            ]
        
        elif task_type == "find_free_slots":
            return [{
                "tool": "find_free_slots",
                "parameters": {
                    "date": params.get("date"),
                    "duration_minutes": params.get("duration", 60),
                    "preferred_time": params.get("preferred_time", "afternoon")
                }
            }]
        
        elif task_type == "check_conflicts":
            return [{
                "tool": "check_conflicts",
                "parameters": {
                    "proposed_time": params.get("time"),
                    "duration_minutes": params.get("duration", 60)
                }
            }]
        
        return []
    
    async def _get_events(
        self,
        start_date: str,
        end_date: str,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """
        Get events from Google Calendar.
        
        In production, this would call the Google Calendar API.
        """
        # Mock response
        events = [
            {
                "id": "evt_001",
                "title": "Team Standup",
                "start": f"{start_date}T09:00:00",
                "end": f"{start_date}T09:30:00",
                "location": "Office",
                "attendees": ["team@company.com"]
            },
            {
                "id": "evt_002",
                "title": "Lunch with Ahmed",
                "start": f"{start_date}T12:30:00",
                "end": f"{start_date}T13:30:00",
                "location": "Restaurant downtown"
            },
            {
                "id": "evt_003",
                "title": "Project Review",
                "start": f"{start_date}T15:00:00",
                "end": f"{start_date}T16:00:00",
                "location": "Conference Room A"
            }
        ]
        
        return {
            "events": events,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "total_events": len(events)
        }
    
    async def _create_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new calendar event."""
        # Mock response
        event_id = f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "event_id": event_id,
            "title": title,
            "start": start_time,
            "end": end_time,
            "location": location,
            "description": description,
            "status": "confirmed",
            "calendar_link": f"https://calendar.google.com/event/{event_id}"
        }
    
    async def _check_conflicts(
        self,
        proposed_time: str,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """Check for conflicts at proposed time."""
        # Mock response - in production, query actual calendar
        return {
            "has_conflict": False,
            "conflicts": [],
            "proposed_time": proposed_time,
            "duration_minutes": duration_minutes,
            "message": "No conflicts found"
        }
    
    async def _find_free_slots(
        self,
        date: str,
        duration_minutes: int,
        preferred_time: str = "afternoon"
    ) -> Dict[str, Any]:
        """Find available time slots."""
        # Mock response
        slots = []
        
        if preferred_time == "morning":
            slots = [
                {"start": f"{date}T08:00:00", "end": f"{date}T09:00:00"},
                {"start": f"{date}T10:00:00", "end": f"{date}T11:00:00"},
            ]
        elif preferred_time == "afternoon":
            slots = [
                {"start": f"{date}T14:00:00", "end": f"{date}T15:00:00"},
                {"start": f"{date}T16:30:00", "end": f"{date}T17:30:00"},
            ]
        else:  # evening
            slots = [
                {"start": f"{date}T18:00:00", "end": f"{date}T19:00:00"},
                {"start": f"{date}T19:30:00", "end": f"{date}T20:30:00"},
            ]
        
        return {
            "date": date,
            "duration_requested": duration_minutes,
            "preferred_time": preferred_time,
            "available_slots": slots,
            "total_slots": len(slots)
        }
]]>
