<![CDATA[#!/usr/bin/env python3
"""
ARIA Demo Scenarios

This script demonstrates various capabilities of the ARIA system
through simulated conversations and workflows.

Run: python demo_scenarios.py
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

# Simulated orchestrator responses for demo
class DemoOrchestrator:
    """
    Simulates the ARIA orchestrator for demonstration purposes.
    In production, this would be the actual LangGraph-based orchestrator.
    """
    
    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user message and return simulated response."""
        message_lower = message.lower()
        
        # Scenario 1: Simple ride booking
        if "uber" in message_lower or "ride" in message_lower:
            return await self._handle_ride_request(message)
        
        # Scenario 2: Medical appointment
        elif "doctor" in message_lower or "dermatologist" in message_lower:
            return await self._handle_medical_request(message)
        
        # Scenario 3: Movie planning
        elif "movie" in message_lower or "cinema" in message_lower:
            return await self._handle_movie_request(message)
        
        # Scenario 4: Complex multi-task request
        elif "and" in message_lower and len(message.split()) > 10:
            return await self._handle_complex_request(message)
        
        # Default response
        return {
            "response": "I understand you want help with something. Could you tell me more specifically what you'd like me to do?",
            "actions": [],
            "requires_confirmation": False
        }
    
    async def _handle_ride_request(self, message: str) -> Dict[str, Any]:
        """Handle ride booking requests."""
        await asyncio.sleep(0.5)  # Simulate processing
        
        return {
            "response": """🚗 I found a ride for you!

**UberX to Cairo Festival City**
• Pickup: Your current location
• ETA: 8 minutes
• Estimated price: $12.50

Driver would be Ahmed M. (⭐ 4.9) in a white Toyota Corolla.

Would you like me to book this ride?""",
            "actions": [{
                "id": "action_ride_001",
                "type": "ride_booking",
                "status": "pending_confirmation",
                "details": {
                    "service": "uber",
                    "ride_type": "UberX",
                    "destination": "Cairo Festival City",
                    "estimated_price": 12.50,
                    "eta_minutes": 8,
                    "driver": {
                        "name": "Ahmed M.",
                        "rating": 4.9,
                        "vehicle": "Toyota Corolla (White)"
                    }
                }
            }],
            "requires_confirmation": True
        }
    
    async def _handle_medical_request(self, message: str) -> Dict[str, Any]:
        """Handle medical appointment requests."""
        await asyncio.sleep(0.8)  # Simulate web scraping delay
        
        return {
            "response": """🏥 I found available dermatologists near you:

**1. Dr. Sarah Ahmed** ⭐ 4.8 (234 reviews)
   📍 Skin Care Center, Nasr City
   💰 300 EGP
   ⏰ Available: Today 3:30 PM, 5:00 PM

**2. Dr. Mohamed Hassan** ⭐ 4.6 (189 reviews)
   📍 Medical Plaza, Downtown
   💰 250 EGP
   ⏰ Available: Tomorrow 11:00 AM

Would you like me to book an appointment with Dr. Sarah Ahmed at 3:30 PM today?""",
            "actions": [{
                "id": "action_medical_001",
                "type": "appointment",
                "status": "pending_confirmation",
                "details": {
                    "doctor": "Dr. Sarah Ahmed",
                    "specialty": "Dermatologist",
                    "time": "Today 3:30 PM",
                    "location": "Skin Care Center, Nasr City",
                    "fee": 300,
                    "currency": "EGP"
                }
            }],
            "requires_confirmation": True
        }
    
    async def _handle_movie_request(self, message: str) -> Dict[str, Any]:
        """Handle movie-related requests."""
        await asyncio.sleep(0.3)
        
        return {
            "response": """🎬 Here's what's showing tonight:

**Dune: Part Two** ⭐ 8.5
• VOX Cinemas City Stars: 6:00 PM (IMAX), 9:30 PM
• Galaxy Mall of Arabia: 7:00 PM (4DX), 10:00 PM

**Oppenheimer** ⭐ 8.4
• VOX Cinemas City Stars: 5:30 PM, 8:45 PM

**Anyone But You** ⭐ 6.3
• Multiple locations: Various times

Would you like me to check your calendar for conflicts and suggest the best showtime?""",
            "actions": [],
            "requires_confirmation": False
        }
    
    async def _handle_complex_request(self, message: str) -> Dict[str, Any]:
        """Handle complex multi-step requests."""
        await asyncio.sleep(1.0)  # Simulate multi-agent processing
        
        return {
            "response": """🧠 Breaking down your request...

✅ **Task 1: Calendar Check**
   Tomorrow 2-6 PM is free

✅ **Task 2: Doctor Search**
   Found Dr. Sarah (Dermatologist)
   Available: 3:30 PM tomorrow
   Location: Skin Care Center, Nasr City

✅ **Task 3: Transport Planning**
   Uber pickup at 3:00 PM would get you there in time
   Estimated cost: $12

📋 **Summary:**
• Appointment: Dr. Sarah, Tomorrow 3:30 PM
• Ride: Uber pickup at 3:00 PM ($12)
• No calendar conflicts detected

Ready to book everything?""",
            "actions": [
                {
                    "id": "action_complex_001",
                    "type": "appointment",
                    "status": "pending_confirmation",
                    "details": {
                        "doctor": "Dr. Sarah",
                        "time": "Tomorrow 3:30 PM"
                    }
                },
                {
                    "id": "action_complex_002",
                    "type": "ride_booking",
                    "status": "pending_confirmation",
                    "details": {
                        "pickup_time": "Tomorrow 3:00 PM",
                        "price": 12
                    }
                }
            ],
            "requires_confirmation": True
        }


async def run_demo():
    """Run interactive demo scenarios."""
    
    print("\n" + "="*60)
    print("🤖 ARIA - Autonomous Reasoning & Intelligent Agent")
    print("="*60)
    print("\nDemo Scenarios:")
    print("1. Simple ride booking")
    print("2. Medical appointment booking")
    print("3. Movie search")
    print("4. Complex multi-task request")
    print("5. Interactive chat (type your own message)")
    print("0. Exit")
    print("-"*60)
    
    orchestrator = DemoOrchestrator()
    
    demo_messages = {
        "1": "Book me an Uber to Cairo Festival City",
        "2": "Find me a dermatologist for tomorrow afternoon",
        "3": "What movies are playing tonight?",
        "4": "I need to see a dermatologist tomorrow, book the appointment and arrange transport to get there",
    }
    
    while True:
        choice = input("\nEnter scenario number (or 5 for custom): ").strip()
        
        if choice == "0":
            print("\nGoodbye! 👋")
            break
        
        if choice == "5":
            message = input("\nYou: ").strip()
            if not message:
                continue
        elif choice in demo_messages:
            message = demo_messages[choice]
            print(f"\nYou: {message}")
        else:
            print("Invalid choice. Please try again.")
            continue
        
        print("\n⏳ ARIA is thinking...\n")
        
        result = await orchestrator.process(message)
        
        print("ARIA:", result["response"])
        
        if result["requires_confirmation"] and result["actions"]:
            confirm = input("\n>>> Confirm action? (y/n): ").strip().lower()
            if confirm == "y":
                print("\n✅ Action confirmed! Executing...")
                await asyncio.sleep(1)
                print("🎉 Done! Your request has been completed.")
            else:
                print("\n❌ Action cancelled.")


def main():
    """Entry point."""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     █████╗ ██████╗ ██╗ █████╗                                ║
    ║    ██╔══██╗██╔══██╗██║██╔══██╗                               ║
    ║    ███████║██████╔╝██║███████║                               ║
    ║    ██╔══██║██╔══██╗██║██╔══██║                               ║
    ║    ██║  ██║██║  ██║██║██║  ██║                               ║
    ║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝                               ║
    ║                                                               ║
    ║    Autonomous Reasoning & Intelligent Agent                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
]]>
