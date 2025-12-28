<![CDATA["""
Reminders API Routes
Manage reminders and notifications.
"""

from typing import Optional, List
from datetime import datetime
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RepeatConfig(BaseModel):
    frequency: str  # once, daily, weekly, monthly
    until: Optional[str] = None


class ReminderCreate(BaseModel):
    message: str
    trigger_time: str
    repeat: Optional[RepeatConfig] = None
    notification_methods: List[str] = ["push"]


@router.get("")
async def list_reminders():
    """
    List all active reminders.
    """
    reminders = [
        {
            "id": "rem_001",
            "message": "Take medication",
            "trigger_time": "2024-01-16T20:00:00Z",
            "repeat": {"frequency": "daily"},
            "notification_methods": ["push"],
            "status": "active",
            "created_at": "2024-01-15T10:00:00Z"
        },
        {
            "id": "rem_002",
            "message": "Call mom",
            "trigger_time": "2024-01-17T18:00:00Z",
            "repeat": None,
            "notification_methods": ["push", "sms"],
            "status": "active",
            "created_at": "2024-01-15T12:00:00Z"
        }
    ]
    
    return {
        "reminders": reminders,
        "total": len(reminders)
    }


@router.post("")
async def create_reminder(reminder: ReminderCreate):
    """
    Create a new reminder.
    """
    reminder_id = f"rem_{uuid.uuid4().hex[:12]}"
    
    return {
        "id": reminder_id,
        "message": reminder.message,
        "trigger_time": reminder.trigger_time,
        "repeat": reminder.repeat.dict() if reminder.repeat else None,
        "notification_methods": reminder.notification_methods,
        "status": "active",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }


@router.get("/{reminder_id}")
async def get_reminder(reminder_id: str):
    """
    Get a specific reminder.
    """
    return {
        "id": reminder_id,
        "message": "Take medication",
        "trigger_time": "2024-01-16T20:00:00Z",
        "repeat": {"frequency": "daily"},
        "notification_methods": ["push"],
        "status": "active",
        "next_trigger": "2024-01-16T20:00:00Z",
        "history": [
            {"triggered_at": "2024-01-15T20:00:00Z", "status": "delivered"},
            {"triggered_at": "2024-01-14T20:00:00Z", "status": "delivered"}
        ]
    }


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str):
    """
    Delete a reminder.
    """
    return {
        "id": reminder_id,
        "status": "deleted",
        "message": "Reminder deleted successfully"
    }


@router.patch("/{reminder_id}")
async def update_reminder(reminder_id: str, updates: dict):
    """
    Update a reminder.
    """
    return {
        "id": reminder_id,
        "status": "updated",
        "message": "Reminder updated successfully",
        "updates_applied": updates
    }
]]>
