<![CDATA["""
Transport Agent
Handles ride booking and transportation services.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.agents.base import BaseAgent, Tool, Task, AgentResult


@dataclass
class Location:
    """Geographic location."""
    latitude: float
    longitude: float
    address: Optional[str] = None


@dataclass
class RideEstimate:
    """Ride price and time estimate."""
    ride_type: str
    price_min: float
    price_max: float
    currency: str
    duration_minutes: int
    distance_km: float
    surge_multiplier: float = 1.0


class TransportAgent(BaseAgent):
    """
    Agent specialized in transportation services.
    
    Capabilities:
    - Get ride estimates
    - Book rides (Uber, Lyft)
    - Track ride status
    - Cancel rides
    - Schedule future pickups
    """
    
    name = "TransportAgent"
    description = "Handles ride booking and transportation logistics"
    
    # Task types this agent can handle
    SUPPORTED_TASKS = [
        "get_ride_estimate",
        "book_ride",
        "track_ride",
        "cancel_ride",
        "schedule_pickup"
    ]
    
    def _initialize_tools(self):
        """Initialize transport-specific tools."""
        self.tools = [
            Tool(
                name="get_ride_estimate",
                description="Get price and time estimate for a ride",
                parameters={
                    "pickup": "Location object or current location",
                    "dropoff": "Location object with destination",
                    "ride_types": "List of ride types to get estimates for"
                },
                function=self._get_estimate,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="book_ride",
                description="Book a ride with selected options",
                parameters={
                    "pickup": "Pickup location",
                    "dropoff": "Dropoff location",
                    "ride_type": "Selected ride type",
                    "scheduled_time": "Optional scheduled pickup time"
                },
                function=self._book_ride,
                requires_confirmation=True,
                estimated_cost=15.0,
                timeout_seconds=60
            ),
            Tool(
                name="get_ride_status",
                description="Get status of an active ride",
                parameters={
                    "ride_id": "ID of the ride to track"
                },
                function=self._get_ride_status,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="cancel_ride",
                description="Cancel a booked ride",
                parameters={
                    "ride_id": "ID of the ride to cancel"
                },
                function=self._cancel_ride,
                requires_confirmation=True,
                timeout_seconds=30
            ),
            Tool(
                name="get_pickup_eta",
                description="Get ETA for driver pickup",
                parameters={
                    "location": "Current location"
                },
                function=self._get_pickup_eta,
                requires_confirmation=False,
                timeout_seconds=15
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the task."""
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create execution plan for transport tasks.
        """
        task_type = task.type
        params = task.parameters
        
        if task_type == "get_ride_estimate":
            return [{
                "tool": "get_ride_estimate",
                "parameters": {
                    "pickup": self._get_current_location(context),
                    "dropoff": params.get("destination"),
                    "ride_types": ["UberX", "UberXL", "UberBlack"]
                }
            }]
        
        elif task_type == "book_ride":
            # First get estimate, then book
            return [
                {
                    "tool": "get_ride_estimate",
                    "parameters": {
                        "pickup": self._get_current_location(context),
                        "dropoff": params.get("destination"),
                        "ride_types": [params.get("ride_type", "UberX")]
                    }
                },
                {
                    "tool": "book_ride",
                    "parameters": {
                        "pickup": self._get_current_location(context),
                        "dropoff": params.get("destination"),
                        "ride_type": params.get("ride_type", "UberX"),
                        "scheduled_time": params.get("pickup_time")
                    }
                }
            ]
        
        elif task_type == "track_ride":
            return [{
                "tool": "get_ride_status",
                "parameters": {
                    "ride_id": params.get("ride_id")
                }
            }]
        
        elif task_type == "cancel_ride":
            return [{
                "tool": "cancel_ride",
                "parameters": {
                    "ride_id": params.get("ride_id")
                }
            }]
        
        elif task_type == "schedule_pickup":
            return [{
                "tool": "book_ride",
                "parameters": {
                    "pickup": self._get_current_location(context),
                    "dropoff": params.get("destination"),
                    "ride_type": params.get("ride_type", "UberX"),
                    "scheduled_time": params.get("pickup_time")
                }
            }]
        
        return []
    
    def _get_current_location(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract current location from context."""
        location = context.get("location", {})
        return {
            "latitude": location.get("lat", 30.0444),  # Default: Cairo
            "longitude": location.get("lng", 31.2357),
            "address": location.get("address", "Current Location")
        }
    
    async def _get_estimate(
        self,
        pickup: Dict[str, Any],
        dropoff: str,
        ride_types: List[str]
    ) -> Dict[str, Any]:
        """
        Get ride estimates from Uber API.
        
        In production, this would call the actual Uber API.
        For demo purposes, returns mock data.
        """
        # Mock response - in production, call Uber API
        estimates = []
        
        base_prices = {
            "UberX": (10, 15),
            "UberXL": (18, 25),
            "UberBlack": (30, 45),
            "UberPool": (6, 10)
        }
        
        for ride_type in ride_types:
            if ride_type in base_prices:
                min_price, max_price = base_prices[ride_type]
                estimates.append({
                    "ride_type": ride_type,
                    "price": {
                        "min": min_price,
                        "max": max_price,
                        "currency": "USD"
                    },
                    "duration_minutes": 25,
                    "distance_km": 15,
                    "surge_multiplier": 1.0
                })
        
        return {
            "estimates": estimates,
            "pickup_eta_minutes": 8,
            "destination": dropoff
        }
    
    async def _book_ride(
        self,
        pickup: Dict[str, Any],
        dropoff: str,
        ride_type: str,
        scheduled_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Book a ride via Uber API.
        
        In production, this would call the actual Uber API.
        """
        # Mock response
        return {
            "ride_id": "ride_uber_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "status": "confirmed",
            "ride_type": ride_type,
            "pickup": pickup,
            "dropoff": dropoff,
            "driver": {
                "name": "Ahmed M.",
                "rating": 4.9,
                "vehicle": "Toyota Corolla",
                "color": "White",
                "plate": "ABC 123"
            },
            "eta_minutes": 8,
            "estimated_price": 12.50,
            "currency": "USD",
            "scheduled_time": scheduled_time
        }
    
    async def _get_ride_status(self, ride_id: str) -> Dict[str, Any]:
        """Get current status of a ride."""
        # Mock response
        return {
            "ride_id": ride_id,
            "status": "driver_en_route",
            "driver": {
                "name": "Ahmed M.",
                "rating": 4.9,
                "location": {
                    "latitude": 30.0500,
                    "longitude": 31.2400
                }
            },
            "eta_minutes": 5,
            "distance_to_pickup_km": 2.3
        }
    
    async def _cancel_ride(self, ride_id: str) -> Dict[str, Any]:
        """Cancel a booked ride."""
        # Mock response
        return {
            "ride_id": ride_id,
            "status": "cancelled",
            "cancellation_fee": 0.0,
            "message": "Ride cancelled successfully"
        }
    
    async def _get_pickup_eta(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get ETA for nearby drivers."""
        # Mock response
        return {
            "etas": {
                "UberX": 5,
                "UberXL": 8,
                "UberBlack": 12
            },
            "location": location
        }
]]>
