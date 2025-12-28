<![CDATA["""
Weather Agent
Provides weather information for planning and recommendations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.agents.base import BaseAgent, Tool, Task


class WeatherAgent(BaseAgent):
    """
    Agent specialized in weather information.
    
    Use Cases:
    - "What's the weather like today?"
    - "Should I bring an umbrella?"
    - "Is it a good day for outdoor activities?"
    - "Plan my week based on weather"
    
    Capabilities:
    - Current weather conditions
    - Multi-day forecasts
    - Weather-based recommendations
    - Severe weather alerts
    """
    
    name = "WeatherAgent"
    description = "Provides weather forecasts and recommendations"
    
    SUPPORTED_TASKS = [
        "get_current_weather",
        "get_forecast",
        "get_weather_alerts",
        "get_activity_recommendation"
    ]
    
    def _initialize_tools(self):
        """Initialize weather-specific tools."""
        self.tools = [
            Tool(
                name="get_current_weather",
                description="Get current weather conditions",
                parameters={
                    "location": "City name or coordinates",
                    "units": "metric or imperial"
                },
                function=self._get_current_weather,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="get_forecast",
                description="Get weather forecast for upcoming days",
                parameters={
                    "location": "City name or coordinates",
                    "days": "Number of days (1-7)",
                    "units": "metric or imperial"
                },
                function=self._get_forecast,
                requires_confirmation=False,
                timeout_seconds=20
            ),
            Tool(
                name="get_weather_alerts",
                description="Check for severe weather alerts",
                parameters={
                    "location": "City name or coordinates"
                },
                function=self._get_alerts,
                requires_confirmation=False,
                timeout_seconds=10
            ),
            Tool(
                name="recommend_activity",
                description="Get activity recommendations based on weather",
                parameters={
                    "location": "City name or coordinates",
                    "activity_type": "outdoor/indoor/any"
                },
                function=self._recommend_activity,
                requires_confirmation=False,
                timeout_seconds=15
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_type = task.type
        params = task.parameters
        location = params.get("location") or self._get_location_from_context(context)
        
        if task_type == "get_current_weather":
            return [{
                "tool": "get_current_weather",
                "parameters": {
                    "location": location,
                    "units": params.get("units", "metric")
                }
            }]
        
        elif task_type == "get_forecast":
            return [{
                "tool": "get_forecast",
                "parameters": {
                    "location": location,
                    "days": params.get("days", 5),
                    "units": params.get("units", "metric")
                }
            }]
        
        elif task_type == "get_weather_alerts":
            return [{
                "tool": "get_weather_alerts",
                "parameters": {"location": location}
            }]
        
        elif task_type == "get_activity_recommendation":
            return [
                {
                    "tool": "get_current_weather",
                    "parameters": {"location": location, "units": "metric"}
                },
                {
                    "tool": "recommend_activity",
                    "parameters": {
                        "location": location,
                        "activity_type": params.get("activity_type", "any")
                    }
                }
            ]
        
        return []
    
    def _get_location_from_context(self, context: Dict[str, Any]) -> str:
        location = context.get("location", {})
        if location.get("address"):
            return location["address"]
        return "Cairo, Egypt"  # Default
    
    async def _get_current_weather(
        self,
        location: str,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        Get current weather from OpenWeatherMap API.
        In production, this calls the actual API.
        """
        # Mock response
        temp_unit = "°C" if units == "metric" else "°F"
        temp = 28 if units == "metric" else 82
        
        return {
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "conditions": {
                "description": "Partly cloudy",
                "icon": "02d",
                "main": "Clouds"
            },
            "temperature": {
                "current": temp,
                "feels_like": temp + 2,
                "unit": temp_unit
            },
            "humidity": 45,
            "wind": {
                "speed": 12,
                "direction": "NE",
                "unit": "km/h" if units == "metric" else "mph"
            },
            "visibility": 10,
            "uv_index": 7,
            "air_quality": {
                "index": 42,
                "level": "Good"
            }
        }
    
    async def _get_forecast(
        self,
        location: str,
        days: int = 5,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """Get weather forecast."""
        temp_unit = "°C" if units == "metric" else "°F"
        base_temp = 28 if units == "metric" else 82
        
        forecast = []
        conditions = ["Sunny", "Partly cloudy", "Cloudy", "Light rain", "Sunny"]
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A"),
                "conditions": conditions[i % len(conditions)],
                "temperature": {
                    "high": base_temp + (i % 3),
                    "low": base_temp - 8 + (i % 2),
                    "unit": temp_unit
                },
                "precipitation_chance": 20 if "rain" in conditions[i % len(conditions)].lower() else 5,
                "humidity": 45 + (i * 2),
                "wind_speed": 10 + i
            })
        
        return {
            "location": location,
            "forecast": forecast,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _get_alerts(self, location: str) -> Dict[str, Any]:
        """Check for weather alerts."""
        # Mock - no alerts
        return {
            "location": location,
            "alerts": [],
            "has_alerts": False,
            "checked_at": datetime.now().isoformat()
        }
    
    async def _recommend_activity(
        self,
        location: str,
        activity_type: str = "any"
    ) -> Dict[str, Any]:
        """Recommend activities based on weather."""
        return {
            "location": location,
            "weather_summary": "Warm and partly cloudy - great for outdoor activities",
            "recommendations": [
                {
                    "activity": "Visit a park or garden",
                    "suitability": "Excellent",
                    "reason": "Pleasant temperature and low chance of rain"
                },
                {
                    "activity": "Outdoor dining",
                    "suitability": "Good",
                    "reason": "Comfortable evening weather expected"
                },
                {
                    "activity": "Morning jog or walk",
                    "suitability": "Excellent",
                    "reason": "Cooler morning temperatures"
                }
            ],
            "warnings": [
                "UV index is high - wear sunscreen if going out midday"
            ]
        }
]]>
