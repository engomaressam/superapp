<![CDATA["""
Reminder Agent
Handles notification and reminder scheduling.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.agents.base import BaseAgent, Tool, Task


class ReminderFrequency(Enum):
    """Reminder repeat frequency."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class NotificationMethod(Enum):
    """Notification delivery method."""
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


class ReminderAgent(BaseAgent):
    """
    Agent specialized in reminders and notifications.
    
    Capabilities:
    - Create reminders
    - Schedule recurring reminders
    - Send notifications via multiple channels
    - Manage reminder history
    """
    
    name = "ReminderAgent"
    description = "Manages reminders and notifications"
    
    SUPPORTED_TASKS = [
        "create_reminder",
        "list_reminders",
        "cancel_reminder",
        "update_reminder",
        "send_notification"
    ]
    
    def _initialize_tools(self):
        """Initialize reminder-specific tools."""
        self.tools = [
            Tool(
                name="create_reminder",
                description="Create a new reminder",
                parameters={
                    "message": "Reminder message",
                    "trigger_time": "When to trigger",
                    "repeat": "Optional repeat settings",
                    "notification_methods": "How to notify"
                },
                function=self._create_reminder,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="list_reminders",
                description="List all active reminders",
                parameters={
                    "filter": "Optional filter criteria"
                },
                function=self._list_reminders,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="cancel_reminder",
                description="Cancel an existing reminder",
                parameters={
                    "reminder_id": "Reminder ID to cancel"
                },
                function=self._cancel_reminder,
                requires_confirmation=True,
                timeout_seconds=15
            ),
            Tool(
                name="send_notification",
                description="Send an immediate notification",
                parameters={
                    "message": "Notification message",
                    "methods": "Notification methods to use",
                    "priority": "Notification priority"
                },
                function=self._send_notification,
                requires_confirmation=False,
                timeout_seconds=30
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the task."""
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution plan for reminder tasks."""
        task_type = task.type
        params = task.parameters
        
        if task_type == "create_reminder":
            return [{
                "tool": "create_reminder",
                "parameters": {
                    "message": params.get("message", "Reminder"),
                    "trigger_time": self._parse_trigger_time(
                        params.get("time"),
                        params.get("date"),
                        context.get("timezone", "UTC")
                    ),
                    "repeat": params.get("repeat"),
                    "notification_methods": params.get("methods", ["push"])
                }
            }]
        
        elif task_type == "list_reminders":
            return [{
                "tool": "list_reminders",
                "parameters": {
                    "filter": params.get("filter")
                }
            }]
        
        elif task_type == "cancel_reminder":
            return [{
                "tool": "cancel_reminder",
                "parameters": {
                    "reminder_id": params.get("reminder_id")
                }
            }]
        
        elif task_type == "send_notification":
            return [{
                "tool": "send_notification",
                "parameters": {
                    "message": params.get("message"),
                    "methods": params.get("methods", ["push"]),
                    "priority": params.get("priority", "normal")
                }
            }]
        
        return []
    
    def _parse_trigger_time(
        self,
        time_str: Optional[str],
        date_str: Optional[str],
        timezone: str
    ) -> str:
        """Parse trigger time from natural language."""
        # Simple parsing - in production, use a proper NLU
        now = datetime.now()
        
        if not time_str and not date_str:
            # Default to 1 hour from now
            trigger = now + timedelta(hours=1)
        elif time_str and not date_str:
            # Time specified, use today
            trigger = now.replace(
                hour=self._parse_hour(time_str),
                minute=0,
                second=0
            )
            # If time has passed, use tomorrow
            if trigger < now:
                trigger += timedelta(days=1)
        else:
            # Both specified
            trigger = datetime.strptime(f"{date_str} {time_str or '09:00'}", "%Y-%m-%d %H:%M")
        
        return trigger.isoformat()
    
    def _parse_hour(self, time_str: str) -> int:
        """Parse hour from time string."""
        time_str = time_str.lower().strip()
        
        # Handle "X pm" or "X am" format
        is_pm = "pm" in time_str
        time_str = time_str.replace("am", "").replace("pm", "").strip()
        
        try:
            if ":" in time_str:
                hour = int(time_str.split(":")[0])
            else:
                hour = int(time_str)
            
            if is_pm and hour < 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0
            
            return hour
        except ValueError:
            return 9  # Default to 9 AM
    
    async def _create_reminder(
        self,
        message: str,
        trigger_time: str,
        repeat: Optional[Dict[str, Any]] = None,
        notification_methods: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new reminder."""
        notification_methods = notification_methods or ["push"]
        
        reminder_id = f"rem_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "reminder_id": reminder_id,
            "message": message,
            "trigger_time": trigger_time,
            "repeat": repeat,
            "notification_methods": notification_methods,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "confirmation": f"Reminder set for {trigger_time}"
        }
    
    async def _list_reminders(
        self,
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List active reminders."""
        # Mock response
        reminders = [
            {
                "id": "rem_001",
                "message": "Take medication",
                "trigger_time": "2024-01-16T20:00:00",
                "repeat": {"frequency": "daily"},
                "status": "active"
            },
            {
                "id": "rem_002",
                "message": "Call mom",
                "trigger_time": "2024-01-17T18:00:00",
                "repeat": None,
                "status": "active"
            },
            {
                "id": "rem_003",
                "message": "Pay rent",
                "trigger_time": "2024-02-01T09:00:00",
                "repeat": {"frequency": "monthly"},
                "status": "active"
            }
        ]
        
        return {
            "reminders": reminders,
            "total": len(reminders),
            "filter_applied": filter
        }
    
    async def _cancel_reminder(
        self,
        reminder_id: str
    ) -> Dict[str, Any]:
        """Cancel an existing reminder."""
        return {
            "reminder_id": reminder_id,
            "status": "cancelled",
            "message": "Reminder cancelled successfully"
        }
    
    async def _send_notification(
        self,
        message: str,
        methods: List[str],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Send an immediate notification."""
        # In production, this would integrate with:
        # - Firebase Cloud Messaging for push
        # - Twilio for SMS
        # - SendGrid/SES for email
        
        results = {}
        
        for method in methods:
            if method == "push":
                results["push"] = {
                    "status": "sent",
                    "delivery_time": datetime.now().isoformat()
                }
            elif method == "sms":
                results["sms"] = {
                    "status": "sent",
                    "message_id": "sms_123456"
                }
            elif method == "email":
                results["email"] = {
                    "status": "sent",
                    "message_id": "email_789012"
                }
        
        return {
            "message": message,
            "priority": priority,
            "delivery_results": results,
            "sent_at": datetime.now().isoformat()
        }
]]>
