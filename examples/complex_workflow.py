<![CDATA[#!/usr/bin/env python3
"""
Complex Workflow Example

Demonstrates multi-agent orchestration for a complex request
that requires coordination between multiple specialized agents.

Example: "Find me a dermatologist for tomorrow, book the appointment,
and arrange transport to get there"
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    type: str
    agent: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = None
    result: Dict[str, Any] = None


class CalendarAgentDemo:
    """Demo calendar agent."""
    
    async def check_availability(self, date: str) -> Dict[str, Any]:
        print("  📅 CalendarAgent: Checking tomorrow's schedule...")
        await asyncio.sleep(0.3)
        return {
            "date": date,
            "available_slots": ["10:00-12:00", "14:00-18:00"],
            "conflicts": [
                {"time": "12:00-14:00", "event": "Lunch Meeting"}
            ]
        }


class MedicalAgentDemo:
    """Demo medical agent."""
    
    async def search_doctors(self, specialty: str) -> Dict[str, Any]:
        print("  🏥 MedicalAgent: Searching for doctors...")
        await asyncio.sleep(0.5)
        return {
            "doctors": [
                {
                    "id": "doc_001",
                    "name": "Dr. Sarah Ahmed",
                    "specialty": specialty,
                    "rating": 4.8,
                    "fee": 300,
                    "available_slots": ["15:00", "16:30"]
                }
            ]
        }
    
    async def book_appointment(self, doctor_id: str, time: str) -> Dict[str, Any]:
        print("  🏥 MedicalAgent: Booking appointment...")
        await asyncio.sleep(0.4)
        return {
            "appointment_id": "apt_12345",
            "doctor": "Dr. Sarah Ahmed",
            "time": time,
            "location": "Skin Care Center, Nasr City",
            "status": "confirmed"
        }


class TransportAgentDemo:
    """Demo transport agent."""
    
    async def plan_ride(self, destination: str, arrival_time: str) -> Dict[str, Any]:
        print("  🚗 TransportAgent: Planning ride...")
        await asyncio.sleep(0.3)
        return {
            "pickup_time": "14:30",  # 30 min before appointment
            "destination": destination,
            "estimated_price": 12,
            "eta_to_destination": 25
        }


class DemoOrchestrator:
    """
    Demonstrates multi-agent orchestration workflow.
    
    This is a simplified version of the LangGraph-based orchestrator.
    """
    
    def __init__(self):
        self.calendar_agent = CalendarAgentDemo()
        self.medical_agent = MedicalAgentDemo()
        self.transport_agent = TransportAgentDemo()
    
    async def process_complex_request(self, request: str) -> Dict[str, Any]:
        """
        Process a complex request through multiple agents.
        
        Flow:
        1. Parse request to identify required agents
        2. Check calendar for availability (CalendarAgent)
        3. Search for doctors (MedicalAgent)
        4. Book appointment (MedicalAgent)
        5. Plan transportation (TransportAgent)
        6. Return consolidated result
        """
        print("\n" + "="*60)
        print("🧠 ARIA Multi-Agent Orchestration Demo")
        print("="*60)
        print(f"\n📝 Request: \"{request}\"\n")
        print("-"*60)
        
        results = {}
        
        # Step 1: Analyze request
        print("\n🔍 Step 1: Analyzing request...")
        await asyncio.sleep(0.2)
        print("   Identified intents: MEDICAL_APPOINTMENT, TRANSPORT")
        print("   Required agents: CalendarAgent, MedicalAgent, TransportAgent")
        
        # Step 2: Check calendar
        print("\n📅 Step 2: Checking calendar availability...")
        calendar_result = await self.calendar_agent.check_availability("tomorrow")
        results["calendar"] = calendar_result
        print(f"   ✅ Available slots: {calendar_result['available_slots']}")
        
        # Step 3: Search doctors
        print("\n🔎 Step 3: Searching for dermatologists...")
        doctor_result = await self.medical_agent.search_doctors("Dermatologist")
        results["doctors"] = doctor_result
        doctor = doctor_result["doctors"][0]
        print(f"   ✅ Found: {doctor['name']} (⭐ {doctor['rating']})")
        print(f"      Fee: {doctor['fee']} EGP")
        print(f"      Available: {doctor['available_slots']}")
        
        # Step 4: Book appointment
        print("\n📋 Step 4: Booking appointment...")
        # Select time that doesn't conflict with calendar
        selected_time = "15:00"  # After lunch meeting
        appointment = await self.medical_agent.book_appointment(
            doctor["id"], 
            selected_time
        )
        results["appointment"] = appointment
        print(f"   ✅ Appointment confirmed!")
        print(f"      Time: {appointment['time']}")
        print(f"      Location: {appointment['location']}")
        
        # Step 5: Plan transport
        print("\n🚗 Step 5: Planning transportation...")
        transport = await self.transport_agent.plan_ride(
            appointment["location"],
            selected_time
        )
        results["transport"] = transport
        print(f"   ✅ Ride planned!")
        print(f"      Pickup: {transport['pickup_time']}")
        print(f"      Price: ${transport['estimated_price']}")
        
        # Compile final result
        print("\n" + "="*60)
        print("📊 FINAL SUMMARY")
        print("="*60)
        print(f"""
✅ All tasks completed successfully!

📋 APPOINTMENT
   Doctor: {appointment['doctor']}
   Time: Tomorrow {appointment['time']}
   Location: {appointment['location']}
   Fee: {doctor['fee']} EGP

🚗 TRANSPORT
   Pickup: Tomorrow {transport['pickup_time']}
   Estimated Cost: ${transport['estimated_price']}

📅 CALENDAR
   No conflicts detected
   Event added to calendar
        """)
        
        return {
            "success": True,
            "summary": "Appointment and transport booked successfully",
            "results": results
        }


async def main():
    """Run the complex workflow demo."""
    
    orchestrator = DemoOrchestrator()
    
    request = (
        "I need to see a dermatologist tomorrow, "
        "book the appointment and arrange transport to get there"
    )
    
    result = await orchestrator.process_complex_request(request)
    
    print("\n" + "-"*60)
    if result["success"]:
        print("🎉 Demo completed successfully!")
    else:
        print("❌ Demo encountered errors")
    print("-"*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
]]>
