<![CDATA["""
Shopping Agent
Handles e-commerce, product search, and price tracking.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.agents.base import BaseAgent, Tool, Task


class ShoppingAgent(BaseAgent):
    """
    Agent specialized in shopping and e-commerce.
    
    Use Cases:
    - "Find me a new iPhone"
    - "Compare prices for AirPods"
    - "Track price of this product"
    - "Add milk to my shopping list"
    - "Order my usual groceries"
    
    Capabilities:
    - Search products across multiple stores
    - Compare prices
    - Track price drops
    - Manage shopping lists
    - Place orders
    - Track deliveries
    """
    
    name = "ShoppingAgent"
    description = "Handles product search, price comparison, and shopping"
    
    SUPPORTED_TASKS = [
        "search_products",
        "compare_prices",
        "track_price",
        "add_to_list",
        "get_shopping_list",
        "place_order",
        "track_package"
    ]
    
    def _initialize_tools(self):
        """Initialize shopping-specific tools."""
        self.tools = [
            Tool(
                name="search_products",
                description="Search for products across stores",
                parameters={
                    "query": "Product search query",
                    "category": "Product category",
                    "filters": "Price range, brand, etc."
                },
                function=self._search_products,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="compare_prices",
                description="Compare prices across different stores",
                parameters={
                    "product_name": "Product to compare",
                    "stores": "List of stores to check"
                },
                function=self._compare_prices,
                requires_confirmation=False,
                timeout_seconds=45
            ),
            Tool(
                name="track_price",
                description="Set up price tracking for a product",
                parameters={
                    "product_id": "Product identifier",
                    "target_price": "Price to alert at",
                    "store": "Store to track"
                },
                function=self._track_price,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="manage_shopping_list",
                description="Add or view shopping list items",
                parameters={
                    "action": "add/remove/view",
                    "items": "Items to add/remove"
                },
                function=self._manage_list,
                requires_confirmation=False,
                timeout_seconds=10
            ),
            Tool(
                name="place_order",
                description="Place an order for products",
                parameters={
                    "products": "List of products to order",
                    "store": "Store to order from",
                    "delivery_address": "Shipping address"
                },
                function=self._place_order,
                requires_confirmation=True,
                estimated_cost=100.0,  # Variable
                timeout_seconds=60
            ),
            Tool(
                name="track_package",
                description="Track a package delivery",
                parameters={
                    "order_id": "Order or tracking number"
                },
                function=self._track_package,
                requires_confirmation=False,
                timeout_seconds=20
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_type = task.type
        params = task.parameters
        
        if task_type == "search_products":
            return [{
                "tool": "search_products",
                "parameters": {
                    "query": params.get("query"),
                    "category": params.get("category"),
                    "filters": params.get("filters", {})
                }
            }]
        
        elif task_type == "compare_prices":
            return [{
                "tool": "compare_prices",
                "parameters": {
                    "product_name": params.get("product_name"),
                    "stores": params.get("stores", ["amazon", "noon", "jumia"])
                }
            }]
        
        elif task_type == "track_price":
            return [{
                "tool": "track_price",
                "parameters": {
                    "product_id": params.get("product_id"),
                    "target_price": params.get("target_price"),
                    "store": params.get("store")
                }
            }]
        
        elif task_type in ["add_to_list", "get_shopping_list"]:
            return [{
                "tool": "manage_shopping_list",
                "parameters": {
                    "action": "add" if task_type == "add_to_list" else "view",
                    "items": params.get("items", [])
                }
            }]
        
        elif task_type == "place_order":
            return [{
                "tool": "place_order",
                "parameters": {
                    "products": params.get("products"),
                    "store": params.get("store"),
                    "delivery_address": params.get("delivery_address")
                }
            }]
        
        elif task_type == "track_package":
            return [{
                "tool": "track_package",
                "parameters": {"order_id": params.get("order_id")}
            }]
        
        return []
    
    async def _search_products(
        self,
        query: str,
        category: str = None,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Search for products."""
        # Mock response (would integrate with Amazon, Noon, etc.)
        products = [
            {
                "id": "prod_001",
                "name": "Apple iPhone 15 Pro Max 256GB",
                "brand": "Apple",
                "price": 62999,
                "original_price": 67999,
                "discount": "7% off",
                "rating": 4.8,
                "reviews": 1250,
                "store": "Noon",
                "availability": "In Stock",
                "delivery": "Tomorrow",
                "image_url": "https://example.com/iphone15.jpg"
            },
            {
                "id": "prod_002",
                "name": "Apple iPhone 15 Pro Max 256GB",
                "brand": "Apple",
                "price": 64500,
                "original_price": 67999,
                "discount": "5% off",
                "rating": 4.7,
                "reviews": 890,
                "store": "Amazon Egypt",
                "availability": "In Stock",
                "delivery": "2-3 days",
                "image_url": "https://example.com/iphone15.jpg"
            },
            {
                "id": "prod_003",
                "name": "Samsung Galaxy S24 Ultra 256GB",
                "brand": "Samsung",
                "price": 54999,
                "original_price": 59999,
                "discount": "8% off",
                "rating": 4.6,
                "reviews": 756,
                "store": "Noon",
                "availability": "In Stock",
                "delivery": "Tomorrow",
                "image_url": "https://example.com/s24.jpg"
            }
        ]
        
        return {
            "query": query,
            "category": category,
            "products": products,
            "total_found": len(products),
            "filters_applied": filters
        }
    
    async def _compare_prices(
        self,
        product_name: str,
        stores: List[str]
    ) -> Dict[str, Any]:
        """Compare prices across stores."""
        comparisons = [
            {
                "store": "Noon",
                "price": 62999,
                "shipping": "Free",
                "delivery": "Tomorrow",
                "total": 62999,
                "in_stock": True,
                "url": "https://noon.com/product/..."
            },
            {
                "store": "Amazon Egypt",
                "price": 64500,
                "shipping": "Free (Prime)",
                "delivery": "2-3 days",
                "total": 64500,
                "in_stock": True,
                "url": "https://amazon.eg/product/..."
            },
            {
                "store": "Jumia",
                "price": 65999,
                "shipping": 50,
                "delivery": "3-5 days",
                "total": 66049,
                "in_stock": True,
                "url": "https://jumia.com.eg/product/..."
            }
        ]
        
        best_price = min(comparisons, key=lambda x: x["total"])
        
        return {
            "product": product_name,
            "comparisons": comparisons,
            "best_deal": {
                "store": best_price["store"],
                "price": best_price["total"],
                "savings": max(c["total"] for c in comparisons) - best_price["total"]
            },
            "currency": "EGP",
            "last_updated": datetime.now().isoformat()
        }
    
    async def _track_price(
        self,
        product_id: str,
        target_price: float,
        store: str
    ) -> Dict[str, Any]:
        """Set up price tracking."""
        return {
            "status": "tracking_active",
            "product_id": product_id,
            "current_price": 62999,
            "target_price": target_price,
            "store": store,
            "price_history": [
                {"date": "2024-01-10", "price": 65999},
                {"date": "2024-01-12", "price": 64500},
                {"date": "2024-01-15", "price": 62999}
            ],
            "notification_settings": {
                "email": True,
                "push": True,
                "sms": False
            },
            "message": f"You'll be notified when price drops to {target_price} EGP or below"
        }
    
    async def _manage_list(
        self,
        action: str,
        items: List[str] = None
    ) -> Dict[str, Any]:
        """Manage shopping list."""
        # Mock shopping list
        shopping_list = [
            {"item": "Milk", "quantity": 2, "category": "Dairy"},
            {"item": "Bread", "quantity": 1, "category": "Bakery"},
            {"item": "Eggs", "quantity": 12, "category": "Dairy"},
            {"item": "Apples", "quantity": 6, "category": "Fruits"},
            {"item": "Chicken breast", "quantity": 1, "category": "Meat"}
        ]
        
        if action == "add" and items:
            for item in items:
                shopping_list.append({"item": item, "quantity": 1, "category": "Other"})
        
        return {
            "action": action,
            "shopping_list": shopping_list,
            "total_items": len(shopping_list),
            "estimated_cost": 450,
            "currency": "EGP",
            "suggested_store": "Carrefour"
        }
    
    async def _place_order(
        self,
        products: List[Dict[str, Any]],
        store: str,
        delivery_address: str
    ) -> Dict[str, Any]:
        """Place an order."""
        order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "order_id": order_id,
            "status": "confirmed",
            "store": store,
            "items": products or [
                {"name": "iPhone 15 Pro Max", "quantity": 1, "price": 62999}
            ],
            "subtotal": 62999,
            "shipping": 0,
            "total": 62999,
            "currency": "EGP",
            "delivery_address": delivery_address,
            "estimated_delivery": "Tomorrow, 2-6 PM",
            "payment_method": "Cash on Delivery",
            "tracking_number": f"TRACK{order_id}",
            "can_cancel": True
        }
    
    async def _track_package(self, order_id: str) -> Dict[str, Any]:
        """Track package delivery."""
        return {
            "order_id": order_id,
            "status": "out_for_delivery",
            "carrier": "Noon Express",
            "tracking_number": f"TRACK{order_id}",
            "history": [
                {"status": "Order placed", "date": "2024-01-14 10:30", "location": "Online"},
                {"status": "Processing", "date": "2024-01-14 14:00", "location": "Warehouse"},
                {"status": "Shipped", "date": "2024-01-15 08:00", "location": "Cairo Hub"},
                {"status": "Out for delivery", "date": "2024-01-15 11:00", "location": "Nasr City"}
            ],
            "estimated_delivery": "Today, 2-4 PM",
            "delivery_address": "Nasr City, Cairo",
            "driver": {
                "name": "Mahmoud",
                "phone": "+20123456789"
            }
        }
]]>
