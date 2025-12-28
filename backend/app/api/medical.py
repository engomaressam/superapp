<![CDATA["""
Medical API Routes
Direct access to healthcare appointment operations.
"""

from typing import Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class DoctorSearch(BaseModel):
    specialty: str
    location: str
    insurance: Optional[str] = None
    date: Optional[str] = None
    sort_by: str = "rating"


class BookAppointment(BaseModel):
    doctor_id: str
    slot: str
    patient_info: dict


@router.post("/search")
async def search_doctors(request: DoctorSearch):
    """
    Search for doctors by specialty and location.
    """
    doctors = [
        {
            "id": "doc_001",
            "name": "Dr. Sarah Ahmed",
            "specialty": request.specialty.title(),
            "clinic": "Skin Care Center",
            "address": "15 Makram Ebeid St, Nasr City",
            "rating": 4.8,
            "reviews_count": 234,
            "consultation_fee": 300,
            "currency": "EGP",
            "available_slots": [
                "2024-01-16T10:00:00",
                "2024-01-16T14:30:00",
                "2024-01-16T16:00:00"
            ],
            "accepts_insurance": ["AXA", "Bupa"],
            "profile_url": "https://vezeeta.com/dr/sarah-ahmed"
        },
        {
            "id": "doc_002",
            "name": "Dr. Mohamed Hassan",
            "specialty": request.specialty.title(),
            "clinic": "Medical Plaza",
            "address": "22 Tahrir St, Downtown",
            "rating": 4.6,
            "reviews_count": 189,
            "consultation_fee": 250,
            "currency": "EGP",
            "available_slots": [
                "2024-01-16T11:00:00",
                "2024-01-16T15:00:00"
            ],
            "accepts_insurance": ["AXA", "MetLife"],
            "profile_url": "https://vezeeta.com/dr/mohamed-hassan"
        }
    ]
    
    # Filter by insurance
    if request.insurance:
        doctors = [d for d in doctors if request.insurance in d["accepts_insurance"]]
    
    # Sort
    if request.sort_by == "rating":
        doctors.sort(key=lambda d: d["rating"], reverse=True)
    elif request.sort_by == "price":
        doctors.sort(key=lambda d: d["consultation_fee"])
    
    return {
        "doctors": doctors,
        "total": len(doctors),
        "source": "vezeeta"
    }


@router.post("/book")
async def book_appointment(request: BookAppointment):
    """
    Book a medical appointment.
    """
    appointment_id = f"apt_{uuid.uuid4().hex[:12]}"
    
    return {
        "appointment_id": appointment_id,
        "status": "confirmed",
        "doctor_id": request.doctor_id,
        "doctor_name": "Dr. Sarah Ahmed",
        "specialty": "Dermatologist",
        "appointment_time": request.slot,
        "clinic": "Skin Care Center",
        "address": "15 Makram Ebeid St, Nasr City",
        "consultation_fee": 300,
        "currency": "EGP",
        "instructions": [
            "Please arrive 15 minutes early",
            "Bring any previous medical records"
        ]
    }


@router.get("/appointments")
async def list_appointments(
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    List user's medical appointments.
    """
    appointments = [
        {
            "id": "apt_001",
            "doctor": "Dr. Sarah Ahmed",
            "specialty": "Dermatologist",
            "datetime": "2024-01-16T14:30:00",
            "clinic": "Skin Care Center",
            "status": "confirmed"
        }
    ]
    
    return {
        "appointments": appointments,
        "total": len(appointments)
    }


@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: str):
    """
    Cancel a medical appointment.
    """
    return {
        "appointment_id": appointment_id,
        "status": "cancelled",
        "message": "Appointment cancelled successfully"
    }
]]>
