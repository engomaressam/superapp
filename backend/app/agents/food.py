<![CDATA["""
Food & Restaurant Agent
Handles food ordering, restaurant bookings, and meal recommendations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.agents.base import BaseAgent, Tool, Task


class FoodAgent(BaseAgent):
    """
    Agent specialized in food-related services.
    
    Use Cases:
    - "Order pizza from the nearest place"
    - "Find a good Italian restaurant nearby"
    - "Book a table for 4 tonight"
    - "What should I eat for dinner?"
    - "Order my usual from McDonald's"
    
    Capabilities:
    - Search restaurants by cuisine/location
    - Order food delivery (Talabat, Uber Eats)
    - Make restaurant reservations
    - Meal recommendations based on preferences
    - Track food orders
    """
    
    name = "FoodAgent"
    description = "Handles food ordering, restaurants, and meal recommendations"
    
    SUPPORTED_TASKS = [
        "search_restaurants",
        "order_food",
        "book_table",
        "track_order",
        "get_recommendations",
        "reorder_favorite"
    ]
    
    def _initialize_tools(self):
        """Initialize food-specific tools."""
        self.tools = [
            Tool(
                name="search_restaurants",
                description="Search for restaurants by cuisine, location, or rating",
                parameters={
                    "query": "Search query or cuisine type",
                    "location": "Delivery address or area",
                    "filters": "Price range, rating, delivery time"
                },
                function=self._search_restaurants,
                requires_confirmation=False,
                timeout_seconds=20
            ),
            Tool(
                name="order_food",
                description="Place a food delivery order",
                parameters={
                    "restaurant_id": "Restaurant identifier",
                    "items": "List of menu items",
                    "delivery_address": "Delivery location",
                    "special_instructions": "Any special requests"
                },
                function=self._order_food,
                requires_confirmation=True,
                estimated_cost=25.0,
                timeout_seconds=45
            ),
            Tool(
                name="book_table",
                description="Make a restaurant reservation",
                parameters={
                    "restaurant_id": "Restaurant identifier",
                    "date": "Reservation date",
                    "time": "Reservation time",
                    "party_size": "Number of guests"
                },
                function=self._book_table,
                requires_confirmation=True,
                timeout_seconds=30
            ),
            Tool(
                name="track_order",
                description="Track a food delivery order",
                parameters={
                    "order_id": "Order identifier"
                },
                function=self._track_order,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="get_meal_recommendations",
                description="Get personalized meal recommendations",
                parameters={
                    "meal_type": "breakfast/lunch/dinner/snack",
                    "preferences": "Dietary preferences",
                    "mood": "What kind of food are you in the mood for"
                },
                function=self._get_recommendations,
                requires_confirmation=False,
                timeout_seconds=15
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_type = task.type
        params = task.parameters
        
        if task_type == "search_restaurants":
            return [{
                "tool": "search_restaurants",
                "parameters": {
                    "query": params.get("query", params.get("cuisine")),
                    "location": params.get("location", context.get("location", {}).get("address")),
                    "filters": params.get("filters", {})
                }
            }]
        
        elif task_type == "order_food":
            steps = []
            
            # If no restaurant specified, search first
            if not params.get("restaurant_id"):
                steps.append({
                    "tool": "search_restaurants",
                    "parameters": {
                        "query": params.get("food_type", ""),
                        "location": params.get("delivery_address")
                    }
                })
            
            steps.append({
                "tool": "order_food",
                "parameters": {
                    "restaurant_id": params.get("restaurant_id", "{previous.restaurants[0].id}"),
                    "items": params.get("items", []),
                    "delivery_address": params.get("delivery_address"),
                    "special_instructions": params.get("special_instructions")
                }
            })
            
            return steps
        
        elif task_type == "book_table":
            return [{
                "tool": "book_table",
                "parameters": {
                    "restaurant_id": params.get("restaurant_id"),
                    "date": params.get("date"),
                    "time": params.get("time"),
                    "party_size": params.get("party_size", 2)
                }
            }]
        
        elif task_type == "track_order":
            return [{
                "tool": "track_order",
                "parameters": {"order_id": params.get("order_id")}
            }]
        
        elif task_type == "get_recommendations":
            return [{
                "tool": "get_meal_recommendations",
                "parameters": {
                    "meal_type": params.get("meal_type", "dinner"),
                    "preferences": params.get("preferences", []),
                    "mood": params.get("mood")
                }
            }]
        
        return []
    
    async def _search_restaurants(
        self,
        query: str,
        location: str,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Search restaurants via food delivery APIs."""
        # Mock response (would integrate with Talabat, Uber Eats, etc.)
        restaurants = [
            {
                "id": "rest_001",
                "name": "Pizza Hut",
                "cuisine": "Italian, Pizza",
                "rating": 4.2,
                "delivery_time": "25-35 min",
                "delivery_fee": 15,
                "minimum_order": 100,
                "distance": "2.3 km",
                "price_range": "$$",
                "offers": ["20% off on orders above 200 EGP"],
                "popular_items": ["Pepperoni Pizza", "Chicken Wings"]
            },
            {
                "id": "rest_002",
                "name": "The Smokery",
                "cuisine": "American, BBQ",
                "rating": 4.6,
                "delivery_time": "30-45 min",
                "delivery_fee": 20,
                "minimum_order": 150,
                "distance": "4.1 km",
                "price_range": "$$$",
                "offers": [],
                "popular_items": ["Smoked Brisket", "BBQ Ribs"]
            },
            {
                "id": "rest_003",
                "name": "Zooba",
                "cuisine": "Egyptian, Street Food",
                "rating": 4.5,
                "delivery_time": "20-30 min",
                "delivery_fee": 10,
                "minimum_order": 80,
                "distance": "1.8 km",
                "price_range": "$$",
                "offers": ["Free delivery on first order"],
                "popular_items": ["Foul", "Taameya", "Hawawshi"]
            }
        ]
        
        return {
            "query": query,
            "location": location,
            "restaurants": restaurants,
            "total_found": len(restaurants),
            "source": "talabat"
        }
    
    async def _order_food(
        self,
        restaurant_id: str,
        items: List[Dict[str, Any]],
        delivery_address: str,
        special_instructions: str = None
    ) -> Dict[str, Any]:
        """Place a food order."""
        order_id = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate total (mock)
        subtotal = 185.00
        delivery_fee = 15.00
        total = subtotal + delivery_fee
        
        return {
            "order_id": order_id,
            "status": "confirmed",
            "restaurant": {
                "id": restaurant_id,
                "name": "Pizza Hut"
            },
            "items": items or [
                {"name": "Large Pepperoni Pizza", "quantity": 1, "price": 145},
                {"name": "Garlic Bread", "quantity": 1, "price": 40}
            ],
            "delivery_address": delivery_address,
            "special_instructions": special_instructions,
            "pricing": {
                "subtotal": subtotal,
                "delivery_fee": delivery_fee,
                "discount": 0,
                "total": total,
                "currency": "EGP"
            },
            "estimated_delivery": "30-40 minutes",
            "payment_method": "Cash on delivery",
            "tracking_url": f"https://talabat.com/track/{order_id}"
        }
    
    async def _book_table(
        self,
        restaurant_id: str,
        date: str,
        time: str,
        party_size: int
    ) -> Dict[str, Any]:
        """Make a restaurant reservation."""
        reservation_id = f"res_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "reservation_id": reservation_id,
            "status": "confirmed",
            "restaurant": {
                "id": restaurant_id,
                "name": "The Smokery",
                "address": "26 July St, Zamalek"
            },
            "date": date,
            "time": time,
            "party_size": party_size,
            "confirmation_code": reservation_id.upper(),
            "notes": "Table will be held for 15 minutes",
            "cancellation_policy": "Free cancellation up to 2 hours before"
        }
    
    async def _track_order(self, order_id: str) -> Dict[str, Any]:
        """Track food delivery order."""
        return {
            "order_id": order_id,
            "status": "on_the_way",
            "status_history": [
                {"status": "confirmed", "time": "10:30"},
                {"status": "preparing", "time": "10:35"},
                {"status": "picked_up", "time": "10:55"},
                {"status": "on_the_way", "time": "11:00"}
            ],
            "driver": {
                "name": "Mohamed",
                "phone": "+20123456789",
                "vehicle": "Motorcycle"
            },
            "estimated_arrival": "11:15",
            "live_tracking_available": True
        }
    
    async def _get_recommendations(
        self,
        meal_type: str,
        preferences: List[str],
        mood: str = None
    ) -> Dict[str, Any]:
        """Get personalized meal recommendations."""
        recommendations = {
            "breakfast": [
                {"name": "Egyptian Foul & Taameya", "restaurant": "Zooba", "why": "Classic Egyptian breakfast"},
                {"name": "Avocado Toast", "restaurant": "Left Bank", "why": "Healthy and filling"}
            ],
            "lunch": [
                {"name": "Grilled Chicken Plate", "restaurant": "Lucille's", "why": "Balanced and satisfying"},
                {"name": "Koshari", "restaurant": "Abou Tarek", "why": "Authentic Egyptian comfort food"}
            ],
            "dinner": [
                {"name": "Mixed Grill", "restaurant": "Abou El Sid", "why": "Great for sharing"},
                {"name": "Seafood Platter", "restaurant": "Fish Market", "why": "Fresh catch of the day"}
            ]
        }
        
        return {
            "meal_type": meal_type,
            "preferences": preferences,
            "recommendations": recommendations.get(meal_type, recommendations["dinner"]),
            "tip": "Based on the weather today, something light would be refreshing!"
        }
]]>
