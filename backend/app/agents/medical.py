<![CDATA["""
Medical Agent
Handles healthcare appointments via web automation.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.agents.base import BaseAgent, Tool, Task


@dataclass
class Doctor:
    """Doctor information."""
    id: str
    name: str
    specialty: str
    clinic: str
    address: str
    rating: float
    consultation_fee: float
    available_slots: List[str]


class MedicalAgent(BaseAgent):
    """
    Agent specialized in healthcare services.
    
    Uses web automation (Playwright) for services like Vezeeta
    that don't have public APIs.
    
    Capabilities:
    - Search for doctors by specialty
    - Check available appointment slots
    - Book medical appointments
    - View appointment history
    """
    
    name = "MedicalAgent"
    description = "Handles medical appointments and healthcare services"
    
    SUPPORTED_TASKS = [
        "find_doctor",
        "book_appointment",
        "check_availability",
        "cancel_appointment",
        "get_appointment_history"
    ]
    
    # Medical specialties for validation
    SPECIALTIES = [
        "dermatologist", "dentist", "cardiologist", "orthopedic",
        "pediatrician", "gynecologist", "ophthalmologist", "ent",
        "neurologist", "psychiatrist", "general practitioner"
    ]
    
    def _initialize_tools(self):
        """Initialize medical-specific tools."""
        self.tools = [
            Tool(
                name="search_doctors",
                description="Search for doctors by specialty and location",
                parameters={
                    "specialty": "Medical specialty",
                    "location": "City or area",
                    "insurance": "Optional insurance provider"
                },
                function=self._search_doctors,
                requires_confirmation=False,
                timeout_seconds=60  # Web automation can be slow
            ),
            Tool(
                name="get_available_slots",
                description="Get available appointment slots for a doctor",
                parameters={
                    "doctor_id": "Doctor's ID",
                    "date": "Preferred date"
                },
                function=self._get_available_slots,
                requires_confirmation=False,
                timeout_seconds=45
            ),
            Tool(
                name="book_appointment",
                description="Book a medical appointment",
                parameters={
                    "doctor_id": "Doctor's ID",
                    "slot_time": "Appointment time",
                    "patient_name": "Patient name",
                    "patient_phone": "Contact phone",
                    "reason": "Reason for visit"
                },
                function=self._book_appointment,
                requires_confirmation=True,
                estimated_cost=50.0,  # Average consultation fee
                timeout_seconds=90
            ),
            Tool(
                name="cancel_appointment",
                description="Cancel a booked appointment",
                parameters={
                    "appointment_id": "Appointment ID"
                },
                function=self._cancel_appointment,
                requires_confirmation=True,
                timeout_seconds=45
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the task."""
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution plan for medical tasks."""
        task_type = task.type
        params = task.parameters
        
        if task_type == "find_doctor":
            return [{
                "tool": "search_doctors",
                "parameters": {
                    "specialty": params.get("specialty", "general practitioner"),
                    "location": params.get("location", "Cairo"),
                    "insurance": params.get("insurance")
                }
            }]
        
        elif task_type == "book_appointment":
            # If doctor_id provided, get slots and book
            # Otherwise, search first
            steps = []
            
            if not params.get("doctor_id"):
                steps.append({
                    "tool": "search_doctors",
                    "parameters": {
                        "specialty": params.get("specialty"),
                        "location": params.get("location", "Cairo")
                    }
                })
            
            steps.append({
                "tool": "get_available_slots",
                "parameters": {
                    "doctor_id": params.get("doctor_id", "{previous.doctors[0].id}"),
                    "date": params.get("date")
                }
            })
            
            steps.append({
                "tool": "book_appointment",
                "parameters": {
                    "doctor_id": params.get("doctor_id", "{previous.doctors[0].id}"),
                    "slot_time": params.get("slot_time", "{previous.slots[0]}"),
                    "patient_name": context.get("user_name", "Patient"),
                    "patient_phone": context.get("user_phone", ""),
                    "reason": params.get("reason", "Consultation")
                }
            })
            
            return steps
        
        elif task_type == "check_availability":
            return [{
                "tool": "get_available_slots",
                "parameters": {
                    "doctor_id": params.get("doctor_id"),
                    "date": params.get("date")
                }
            }]
        
        elif task_type == "cancel_appointment":
            return [{
                "tool": "cancel_appointment",
                "parameters": {
                    "appointment_id": params.get("appointment_id")
                }
            }]
        
        return []
    
    async def _search_doctors(
        self,
        specialty: str,
        location: str,
        insurance: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for doctors on Vezeeta.
        
        In production, this would use Playwright for web automation.
        """
        # Mock response - in production, scrape Vezeeta
        doctors = [
            {
                "id": "doc_001",
                "name": "Dr. Sarah Ahmed",
                "specialty": specialty.title(),
                "clinic": "Skin Care Center",
                "address": "15 Makram Ebeid St, Nasr City",
                "rating": 4.8,
                "reviews_count": 234,
                "consultation_fee": 300,
                "currency": "EGP",
                "available_today": True,
                "next_available": "2024-01-16T14:30:00",
                "accepts_insurance": ["AXA", "Bupa", "Allianz"],
                "profile_url": "https://vezeeta.com/dr/sarah-ahmed"
            },
            {
                "id": "doc_002",
                "name": "Dr. Mohamed Hassan",
                "specialty": specialty.title(),
                "clinic": "Medical Plaza",
                "address": "22 Tahrir St, Downtown",
                "rating": 4.6,
                "reviews_count": 189,
                "consultation_fee": 250,
                "currency": "EGP",
                "available_today": True,
                "next_available": "2024-01-16T11:00:00",
                "accepts_insurance": ["AXA", "MetLife"],
                "profile_url": "https://vezeeta.com/dr/mohamed-hassan"
            },
            {
                "id": "doc_003",
                "name": "Dr. Laila Mahmoud",
                "specialty": specialty.title(),
                "clinic": "Elite Medical Center",
                "address": "Mall of Arabia, 6th October",
                "rating": 4.9,
                "reviews_count": 312,
                "consultation_fee": 400,
                "currency": "EGP",
                "available_today": False,
                "next_available": "2024-01-17T10:00:00",
                "accepts_insurance": ["Bupa", "Allianz", "Cigna"],
                "profile_url": "https://vezeeta.com/dr/laila-mahmoud"
            }
        ]
        
        # Filter by insurance if specified
        if insurance:
            doctors = [
                d for d in doctors 
                if insurance in d.get("accepts_insurance", [])
            ]
        
        return {
            "specialty": specialty,
            "location": location,
            "insurance_filter": insurance,
            "doctors": doctors,
            "total_found": len(doctors),
            "source": "vezeeta"
        }
    
    async def _get_available_slots(
        self,
        doctor_id: str,
        date: str
    ) -> Dict[str, Any]:
        """Get available appointment slots."""
        # Mock response
        slots = [
            f"{date}T10:00:00",
            f"{date}T11:30:00",
            f"{date}T14:00:00",
            f"{date}T15:30:00",
            f"{date}T17:00:00"
        ]
        
        return {
            "doctor_id": doctor_id,
            "date": date,
            "available_slots": slots,
            "total_slots": len(slots),
            "consultation_duration_minutes": 30
        }
    
    async def _book_appointment(
        self,
        doctor_id: str,
        slot_time: str,
        patient_name: str,
        patient_phone: str,
        reason: str = "Consultation"
    ) -> Dict[str, Any]:
        """Book a medical appointment."""
        # Mock response
        appointment_id = f"apt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "appointment_id": appointment_id,
            "status": "confirmed",
            "doctor_id": doctor_id,
            "doctor_name": "Dr. Sarah Ahmed",  # Would come from actual booking
            "specialty": "Dermatologist",
            "appointment_time": slot_time,
            "clinic": "Skin Care Center",
            "address": "15 Makram Ebeid St, Nasr City",
            "patient_name": patient_name,
            "consultation_fee": 300,
            "currency": "EGP",
            "instructions": [
                "Please arrive 15 minutes early",
                "Bring any previous medical records",
                "Wear comfortable clothing for examination"
            ],
            "confirmation_sent_to": patient_phone
        }
    
    async def _cancel_appointment(
        self,
        appointment_id: str
    ) -> Dict[str, Any]:
        """Cancel a booked appointment."""
        # Mock response
        return {
            "appointment_id": appointment_id,
            "status": "cancelled",
            "refund_amount": 0,
            "cancellation_fee": 0,
            "message": "Appointment cancelled successfully. No charges applied."
        }
]]>
