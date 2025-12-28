<![CDATA[#!/usr/bin/env python3
"""
Simple Task Example

Demonstrates how to use ARIA agents for a single task.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Any

# Mock implementations for demo
@dataclass
class Task:
    id: str
    type: str
    parameters: Dict[str, Any]

@dataclass
class AgentResult:
    success: bool
    data: Dict[str, Any]
    error: str = None


class TransportAgentDemo:
    """Simplified transport agent for demonstration."""
    
    async def execute(self, task: Task) -> AgentResult:
        """Execute a transport-related task."""
        print(f"🚗 TransportAgent executing: {task.type}")
        
        if task.type == "get_ride_estimate":
            await asyncio.sleep(0.5)  # Simulate API call
            return AgentResult(
                success=True,
                data={
                    "estimates": [
                        {"type": "UberX", "price": 12.50, "eta": 8},
                        {"type": "UberXL", "price": 18.00, "eta": 12},
                    ],
                    "destination": task.parameters.get("destination")
                }
            )
        
        elif task.type == "book_ride":
            await asyncio.sleep(0.8)  # Simulate booking
            return AgentResult(
                success=True,
                data={
                    "ride_id": "ride_12345",
                    "status": "confirmed",
                    "driver": "Ahmed M.",
                    "eta": 8,
                    "price": task.parameters.get("price", 12.50)
                }
            )
        
        return AgentResult(success=False, data={}, error="Unknown task type")


async def main():
    """Run a simple ride booking workflow."""
    
    print("\n" + "="*50)
    print("📱 ARIA Simple Task Demo")
    print("="*50 + "\n")
    
    agent = TransportAgentDemo()
    
    # Step 1: Get estimate
    print("Step 1: Getting ride estimate...")
    estimate_task = Task(
        id="task_001",
        type="get_ride_estimate",
        parameters={
            "destination": "Cairo Festival City",
            "pickup": "Current Location"
        }
    )
    
    estimate_result = await agent.execute(estimate_task)
    
    if estimate_result.success:
        print("✅ Estimate received:")
        for est in estimate_result.data["estimates"]:
            print(f"   • {est['type']}: ${est['price']} ({est['eta']} min)")
    else:
        print(f"❌ Error: {estimate_result.error}")
        return
    
    print()
    
    # Step 2: Book ride
    print("Step 2: Booking ride...")
    book_task = Task(
        id="task_002",
        type="book_ride",
        parameters={
            "destination": "Cairo Festival City",
            "ride_type": "UberX",
            "price": 12.50
        }
    )
    
    book_result = await agent.execute(book_task)
    
    if book_result.success:
        print("✅ Ride booked!")
        print(f"   • Ride ID: {book_result.data['ride_id']}")
        print(f"   • Driver: {book_result.data['driver']}")
        print(f"   • ETA: {book_result.data['eta']} minutes")
        print(f"   • Price: ${book_result.data['price']}")
    else:
        print(f"❌ Error: {book_result.error}")
    
    print("\n" + "="*50)
    print("Demo complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
]]>
