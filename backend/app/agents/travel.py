<![CDATA["""
Travel Agent
Handles flight bookings, hotels, and trip planning.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.agents.base import BaseAgent, Tool, Task


class TravelAgent(BaseAgent):
    """
    Agent for travel planning and bookings.
    
    Use Cases:
    - "Find flights to Dubai next weekend"
    - "Book a hotel near the beach in Hurghada"
    - "Plan a 5-day trip to Turkey"
    - "What's the best time to visit Luxor?"
    
    Capabilities:
    - Flight search and booking
    - Hotel reservations
    - Trip planning and itineraries
    - Travel recommendations
    """
    
    name = "TravelAgent"
    description = "Plans trips, books flights and hotels"
    
    SUPPORTED_TASKS = [
        "search_flights",
        "search_hotels",
        "book_flight",
        "book_hotel",
        "plan_trip",
        "get_travel_info"
    ]
    
    def _initialize_tools(self):
        self.tools = [
            Tool(
                name="search_flights",
                description="Search for flights",
                parameters={
                    "origin": "Departure city",
                    "destination": "Arrival city",
                    "departure_date": "Date",
                    "return_date": "Optional return"
                },
                function=self._search_flights,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="search_hotels",
                description="Search for hotels",
                parameters={
                    "destination": "City",
                    "check_in": "Check-in date",
                    "check_out": "Check-out date",
                    "guests": "Number of guests"
                },
                function=self._search_hotels,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="book_flight",
                description="Book a flight",
                parameters={"flight_id": "Flight to book"},
                function=self._book_flight,
                requires_confirmation=True,
                estimated_cost=500.0,
                timeout_seconds=60
            ),
            Tool(
                name="plan_trip",
                description="Create trip itinerary",
                parameters={
                    "destination": "Where to go",
                    "duration": "Trip length",
                    "interests": "Travel interests"
                },
                function=self._plan_trip,
                requires_confirmation=False,
                timeout_seconds=45
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        params = task.parameters
        if task.type == "search_flights":
            return [{"tool": "search_flights", "parameters": params}]
        elif task.type == "search_hotels":
            return [{"tool": "search_hotels", "parameters": params}]
        elif task.type == "plan_trip":
            return [{"tool": "plan_trip", "parameters": params}]
        return []
    
    async def _search_flights(
        self, origin: str, destination: str,
        departure_date: str, return_date: str = None
    ) -> Dict[str, Any]:
        return {
            "flights": [
                {
                    "id": "FLT001",
                    "airline": "EgyptAir",
                    "departure": f"{departure_date}T08:00",
                    "arrival": f"{departure_date}T12:00",
                    "price": 4500,
                    "class": "Economy",
                    "stops": 0
                },
                {
                    "id": "FLT002",
                    "airline": "Emirates",
                    "departure": f"{departure_date}T14:30",
                    "arrival": f"{departure_date}T18:30",
                    "price": 6200,
                    "class": "Economy",
                    "stops": 0
                }
            ],
            "currency": "EGP"
        }
    
    async def _search_hotels(
        self, destination: str, check_in: str,
        check_out: str, guests: int = 2
    ) -> Dict[str, Any]:
        return {
            "hotels": [
                {
                    "id": "HTL001",
                    "name": "Marriott Hotel",
                    "rating": 4.5,
                    "price_per_night": 2500,
                    "amenities": ["Pool", "Gym", "Spa"]
                },
                {
                    "id": "HTL002",
                    "name": "Hilton Resort",
                    "rating": 4.7,
                    "price_per_night": 3200,
                    "amenities": ["Beach", "Pool", "Restaurant"]
                }
            ],
            "currency": "EGP"
        }
    
    async def _book_flight(self, flight_id: str) -> Dict[str, Any]:
        return {
            "booking_ref": f"BK{datetime.now().strftime('%Y%m%d%H%M')}",
            "status": "confirmed",
            "flight_id": flight_id,
            "e_ticket": "Will be sent to your email"
        }
    
    async def _plan_trip(
        self, destination: str, duration: int, interests: List[str] = None
    ) -> Dict[str, Any]:
        return {
            "destination": destination,
            "duration": f"{duration} days",
            "itinerary": [
                {"day": 1, "activities": ["Arrival", "Hotel check-in", "City walk"]},
                {"day": 2, "activities": ["Local tour", "Cultural sites", "Local cuisine"]},
                {"day": 3, "activities": ["Beach/Nature", "Shopping", "Departure"]}
            ],
            "estimated_budget": {"flights": 5000, "hotel": 4500, "activities": 2000},
            "tips": ["Best time: Spring/Fall", "Visa: Check requirements"]
        }
]]>
