<![CDATA["""
Smart Home Agent
Controls IoT devices and home automation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.agents.base import BaseAgent, Tool, Task


class SmartHomeAgent(BaseAgent):
    """
    Agent specialized in smart home control.
    
    Use Cases:
    - "Turn off all the lights"
    - "Set the AC to 22 degrees"
    - "Is anyone home?"
    - "Lock all doors"
    - "What's the temperature inside?"
    - "Arm the security system"
    
    Capabilities:
    - Control lights (on/off, brightness, color)
    - Climate control (AC, heating, fans)
    - Security (locks, cameras, alarm)
    - Entertainment (TV, speakers)
    - Scenes and routines
    - Energy monitoring
    
    Integrations:
    - Google Home
    - Amazon Alexa
    - Apple HomeKit
    - Samsung SmartThings
    """
    
    name = "SmartHomeAgent"
    description = "Controls smart home devices and automation"
    
    SUPPORTED_TASKS = [
        "control_lights",
        "control_climate",
        "control_security",
        "get_device_status",
        "activate_scene",
        "get_energy_usage"
    ]
    
    def _initialize_tools(self):
        """Initialize smart home tools."""
        self.tools = [
            Tool(
                name="control_lights",
                description="Control smart lights",
                parameters={
                    "room": "Room or 'all'",
                    "action": "on/off/dim/color",
                    "value": "Brightness (0-100) or color"
                },
                function=self._control_lights,
                requires_confirmation=False,
                timeout_seconds=10
            ),
            Tool(
                name="control_climate",
                description="Control AC, heating, and fans",
                parameters={
                    "device": "Device type",
                    "action": "on/off/set_temp/mode",
                    "value": "Temperature or mode"
                },
                function=self._control_climate,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="control_security",
                description="Control locks, cameras, and alarm",
                parameters={
                    "device": "lock/camera/alarm",
                    "action": "lock/unlock/arm/disarm/view"
                },
                function=self._control_security,
                requires_confirmation=True,  # Security actions need confirmation
                timeout_seconds=15
            ),
            Tool(
                name="get_device_status",
                description="Get status of smart devices",
                parameters={
                    "device_type": "Type of device or 'all'",
                    "room": "Specific room or 'all'"
                },
                function=self._get_device_status,
                requires_confirmation=False,
                timeout_seconds=20
            ),
            Tool(
                name="activate_scene",
                description="Activate a predefined scene/routine",
                parameters={
                    "scene_name": "Name of scene"
                },
                function=self._activate_scene,
                requires_confirmation=False,
                timeout_seconds=15
            ),
            Tool(
                name="get_energy_usage",
                description="Get energy consumption data",
                parameters={
                    "period": "today/week/month"
                },
                function=self._get_energy_usage,
                requires_confirmation=False,
                timeout_seconds=15
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_type = task.type
        params = task.parameters
        
        if task_type == "control_lights":
            return [{
                "tool": "control_lights",
                "parameters": {
                    "room": params.get("room", "all"),
                    "action": params.get("action", "on"),
                    "value": params.get("value")
                }
            }]
        
        elif task_type == "control_climate":
            return [{
                "tool": "control_climate",
                "parameters": {
                    "device": params.get("device", "ac"),
                    "action": params.get("action", "set_temp"),
                    "value": params.get("value", 24)
                }
            }]
        
        elif task_type == "control_security":
            return [{
                "tool": "control_security",
                "parameters": {
                    "device": params.get("device", "alarm"),
                    "action": params.get("action")
                }
            }]
        
        elif task_type == "get_device_status":
            return [{
                "tool": "get_device_status",
                "parameters": {
                    "device_type": params.get("device_type", "all"),
                    "room": params.get("room", "all")
                }
            }]
        
        elif task_type == "activate_scene":
            return [{
                "tool": "activate_scene",
                "parameters": {
                    "scene_name": params.get("scene_name")
                }
            }]
        
        elif task_type == "get_energy_usage":
            return [{
                "tool": "get_energy_usage",
                "parameters": {
                    "period": params.get("period", "today")
                }
            }]
        
        return []
    
    async def _control_lights(
        self,
        room: str,
        action: str,
        value: Any = None
    ) -> Dict[str, Any]:
        """Control smart lights."""
        affected_devices = []
        
        if room == "all":
            rooms = ["living_room", "bedroom", "kitchen", "bathroom"]
        else:
            rooms = [room]
        
        for r in rooms:
            affected_devices.append({
                "device": f"{r}_light",
                "room": r.replace("_", " ").title(),
                "previous_state": "on" if action == "off" else "off",
                "new_state": action,
                "brightness": value if action == "dim" else (100 if action == "on" else 0)
            })
        
        return {
            "status": "success",
            "action": action,
            "affected_devices": affected_devices,
            "message": f"Lights in {room} turned {action}"
        }
    
    async def _control_climate(
        self,
        device: str,
        action: str,
        value: Any = None
    ) -> Dict[str, Any]:
        """Control climate devices."""
        return {
            "status": "success",
            "device": device,
            "action": action,
            "settings": {
                "temperature": value if action == "set_temp" else 24,
                "mode": value if action == "mode" else "cool",
                "fan_speed": "auto",
                "power": "on" if action in ["on", "set_temp"] else "off"
            },
            "current_room_temp": 28,
            "target_temp": value if action == "set_temp" else 24,
            "estimated_time_to_target": "15 minutes",
            "message": f"AC set to {value}°C" if action == "set_temp" else f"AC turned {action}"
        }
    
    async def _control_security(
        self,
        device: str,
        action: str
    ) -> Dict[str, Any]:
        """Control security devices."""
        results = {
            "lock": {
                "lock": {
                    "status": "success",
                    "devices": [
                        {"name": "Front Door", "status": "locked"},
                        {"name": "Back Door", "status": "locked"},
                        {"name": "Garage", "status": "locked"}
                    ],
                    "message": "All doors locked"
                },
                "unlock": {
                    "status": "success",
                    "devices": [
                        {"name": "Front Door", "status": "unlocked"}
                    ],
                    "message": "Front door unlocked",
                    "auto_lock": "Door will auto-lock in 5 minutes"
                }
            },
            "alarm": {
                "arm": {
                    "status": "success",
                    "mode": "away",
                    "armed_zones": ["perimeter", "motion", "glass_break"],
                    "message": "Security system armed",
                    "exit_delay": "60 seconds"
                },
                "disarm": {
                    "status": "success",
                    "message": "Security system disarmed"
                }
            },
            "camera": {
                "view": {
                    "status": "success",
                    "cameras": [
                        {"name": "Front Door", "status": "online", "recording": True},
                        {"name": "Backyard", "status": "online", "recording": True},
                        {"name": "Living Room", "status": "online", "recording": False}
                    ],
                    "stream_url": "https://camera.example.com/live"
                }
            }
        }
        
        return results.get(device, {}).get(action, {"status": "unknown_action"})
    
    async def _get_device_status(
        self,
        device_type: str,
        room: str
    ) -> Dict[str, Any]:
        """Get status of all devices."""
        return {
            "status": "success",
            "devices": {
                "lights": [
                    {"name": "Living Room Light", "status": "on", "brightness": 75},
                    {"name": "Bedroom Light", "status": "off", "brightness": 0},
                    {"name": "Kitchen Light", "status": "on", "brightness": 100}
                ],
                "climate": [
                    {"name": "Living Room AC", "status": "on", "temperature": 24, "mode": "cool"},
                    {"name": "Bedroom AC", "status": "off"}
                ],
                "security": {
                    "alarm": {"status": "armed", "mode": "home"},
                    "locks": [
                        {"name": "Front Door", "status": "locked"},
                        {"name": "Back Door", "status": "locked"}
                    ],
                    "cameras": [
                        {"name": "Front Camera", "status": "online"}
                    ]
                },
                "sensors": {
                    "temperature": {"value": 26, "unit": "°C", "location": "Living Room"},
                    "humidity": {"value": 45, "unit": "%"},
                    "motion": {"last_detected": "2 minutes ago", "location": "Kitchen"}
                }
            },
            "summary": {
                "total_devices": 12,
                "online": 12,
                "offline": 0,
                "active": 5
            }
        }
    
    async def _activate_scene(self, scene_name: str) -> Dict[str, Any]:
        """Activate a scene/routine."""
        scenes = {
            "good_morning": {
                "actions": [
                    "Lights on at 70% in bedroom",
                    "AC set to 24°C",
                    "Coffee maker started",
                    "Blinds opened"
                ],
                "message": "Good morning! Your home is ready for the day."
            },
            "good_night": {
                "actions": [
                    "All lights off",
                    "AC set to 22°C",
                    "Doors locked",
                    "Alarm armed (night mode)",
                    "TV off"
                ],
                "message": "Good night! Sweet dreams."
            },
            "movie_time": {
                "actions": [
                    "Living room lights dimmed to 20%",
                    "TV turned on",
                    "Blinds closed",
                    "AC set to 23°C"
                ],
                "message": "Enjoy your movie!"
            },
            "leaving_home": {
                "actions": [
                    "All lights off",
                    "AC off",
                    "All doors locked",
                    "Alarm armed (away mode)",
                    "Robot vacuum started"
                ],
                "message": "Home secured. Have a great day!"
            },
            "arriving_home": {
                "actions": [
                    "Front door unlocked",
                    "Hallway lights on",
                    "AC turned on",
                    "Alarm disarmed"
                ],
                "message": "Welcome home!"
            }
        }
        
        scene = scenes.get(scene_name.lower().replace(" ", "_"), {
            "actions": ["Scene not found"],
            "message": f"Scene '{scene_name}' not configured"
        })
        
        return {
            "status": "success",
            "scene": scene_name,
            "actions_executed": scene["actions"],
            "message": scene["message"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_energy_usage(self, period: str) -> Dict[str, Any]:
        """Get energy consumption data."""
        usage_data = {
            "today": {
                "total_kwh": 12.5,
                "cost": 18.75,
                "breakdown": {
                    "AC": {"kwh": 6.2, "percentage": 50},
                    "Lights": {"kwh": 1.8, "percentage": 14},
                    "Kitchen Appliances": {"kwh": 2.5, "percentage": 20},
                    "Entertainment": {"kwh": 1.2, "percentage": 10},
                    "Other": {"kwh": 0.8, "percentage": 6}
                }
            },
            "week": {
                "total_kwh": 85.3,
                "cost": 127.95,
                "daily_average": 12.2
            },
            "month": {
                "total_kwh": 342.0,
                "cost": 513.00,
                "comparison": {
                    "vs_last_month": "-5%",
                    "vs_same_month_last_year": "-12%"
                }
            }
        }
        
        return {
            "period": period,
            "usage": usage_data.get(period, usage_data["today"]),
            "currency": "EGP",
            "tips": [
                "AC is your biggest energy consumer. Consider raising the temp by 1°C to save 10%",
                "Your usage is below average for homes your size"
            ]
        }
]]>
