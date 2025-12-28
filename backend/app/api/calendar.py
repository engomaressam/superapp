<![CDATA["""
Calendar API Routes
Direct access to calendar operations.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class EventCreate(BaseModel):
    title: str
    start: str  # ISO 8601
    end: str    # ISO 8601
    location: Optional[str] = None
    description: Optional[str] = None
    reminders: Optional[List[dict]] = None


class AvailabilityRequest(BaseModel):
    date: str
    duration_minutes: int = 60
    preferred_times: List[str] = ["morning", "afternoon"]


@router.get("/events")
async def get_events(
    start_date: str = Query(..., description="Start date (ISO 8601)"),
    end_date: str = Query(..., description="End date (ISO 8601)"),
    calendar_id: Optional[str] = Query(None, description="Calendar ID")
):
    """
    Get calendar events for a date range.
    """
    # Mock response
    return {
        "events": [
            {
                "id": "evt_001",
                "title": "Team Meeting",
                "start": f"{start_date}T10:00:00Z",
                "end": f"{start_date}T11:00:00Z",
                "location": "Office",
                "calendar": "Work",
                "attendees": ["john@example.com"],
                "reminders": [{"minutes": 30, "method": "popup"}]
            }
        ]
    }


@router.post("/events")
async def create_event(event: EventCreate):
    """
    Create a new calendar event.
    """
    event_id = f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "id": event_id,
        "title": event.title,
        "start": event.start,
        "end": event.end,
        "location": event.location,
        "description": event.description,
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }


@router.post("/availability")
async def check_availability(request: AvailabilityRequest):
    """
    Check calendar availability and find free slots.
    """
    date = request.date
    
    available_slots = []
    
    if "morning" in request.preferred_times:
        available_slots.extend([
            {"start": f"{date}T09:00:00Z", "end": f"{date}T10:00:00Z", "preference_match": "morning"},
            {"start": f"{date}T10:30:00Z", "end": f"{date}T11:30:00Z", "preference_match": "morning"}
        ])
    
    if "afternoon" in request.preferred_times:
        available_slots.extend([
            {"start": f"{date}T14:00:00Z", "end": f"{date}T15:00:00Z", "preference_match": "afternoon"},
            {"start": f"{date}T16:00:00Z", "end": f"{date}T17:00:00Z", "preference_match": "afternoon"}
        ])
    
    return {
        "available_slots": available_slots,
        "conflicts": [
            {"time": f"{date}T12:00:00Z", "event": "Lunch Meeting"}
        ]
    }
]]>
