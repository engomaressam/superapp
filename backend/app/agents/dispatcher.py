<![CDATA["""
Dispatcher Agent
Analyzes user intent and creates execution plans.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import structlog

logger = structlog.get_logger()


class IntentType(Enum):
    """Types of user intents."""
    TRANSPORT = "transport"
    CALENDAR = "calendar"
    MEDICAL = "medical"
    MOVIE = "movie"
    REMINDER = "reminder"
    MULTI = "multi"  # Multiple intents
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Parsed user intent."""
    type: IntentType
    confidence: float
    entities: Dict[str, Any]
    sub_intents: List['Intent'] = None


class DispatcherAgent:
    """
    The Dispatcher Agent analyzes user requests and creates execution plans.
    
    Responsibilities:
    1. Parse natural language into structured intents
    2. Decompose complex requests into subtasks
    3. Assign tasks to appropriate specialized agents
    4. Generate user-friendly responses
    """
    
    # Intent keywords for rule-based fallback
    INTENT_KEYWORDS = {
        IntentType.TRANSPORT: [
            "uber", "ride", "taxi", "cab", "pickup", "drop", 
            "book a ride", "car", "lyft", "transport"
        ],
        IntentType.CALENDAR: [
            "calendar", "schedule", "appointment", "meeting", 
            "event", "free time", "busy", "available", "slot"
        ],
        IntentType.MEDICAL: [
            "doctor", "medical", "hospital", "clinic", "vezeeta",
            "dermatologist", "dentist", "appointment", "health"
        ],
        IntentType.MOVIE: [
            "movie", "cinema", "film", "showtime", "theater",
            "watching", "tickets"
        ],
        IntentType.REMINDER: [
            "remind", "reminder", "notify", "alert", "remember",
            "don't forget", "notification"
        ],
    }
    
    def __init__(self, llm_client=None):
        """
        Initialize the dispatcher.
        
        Args:
            llm_client: Optional LLM client for advanced NLU
        """
        self.llm = llm_client
    
    async def analyze_intent(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze user message to determine intent.
        
        Args:
            message: User's natural language input
            context: Additional context (location, time, etc.)
            
        Returns:
            Dictionary with intent analysis
        """
        context = context or {}
        
        # Try LLM-based analysis first
        if self.llm:
            try:
                return await self._analyze_with_llm(message, context)
            except Exception as e:
                logger.warning("LLM analysis failed, using fallback", error=str(e))
        
        # Fallback to rule-based analysis
        return self._analyze_with_rules(message, context)
    
    async def _analyze_with_llm(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM for intent analysis.
        """
        system_prompt = """You are an intent analysis system for a personal AI assistant.
        
Analyze the user's message and extract:
1. Primary intent (transport, calendar, medical, movie, reminder)
2. Entities (dates, times, locations, names, etc.)
3. Whether multiple intents are present

Respond in JSON format:
{
    "type": "transport|calendar|medical|movie|reminder|multi",
    "confidence": 0.0-1.0,
    "entities": {
        "date": "optional",
        "time": "optional",
        "location": "optional",
        "destination": "optional",
        "specialty": "optional (for medical)",
        "movie_name": "optional"
    },
    "sub_intents": [] // if type is "multi"
}"""

        # This would call the actual LLM
        # response = await self.llm.complete(system_prompt, message)
        # return json.loads(response)
        
        # Placeholder - in production, this calls the LLM
        return self._analyze_with_rules(message, context)
    
    def _analyze_with_rules(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rule-based intent analysis as fallback.
        """
        message_lower = message.lower()
        detected_intents = []
        
        # Check for each intent type
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    detected_intents.append(intent_type)
                    break
        
        # Remove duplicates while preserving order
        detected_intents = list(dict.fromkeys(detected_intents))
        
        if not detected_intents:
            return {
                "type": IntentType.UNKNOWN.value,
                "confidence": 0.3,
                "entities": self._extract_entities(message),
                "sub_intents": []
            }
        
        if len(detected_intents) == 1:
            return {
                "type": detected_intents[0].value,
                "confidence": 0.8,
                "entities": self._extract_entities(message),
                "sub_intents": []
            }
        
        # Multiple intents
        return {
            "type": IntentType.MULTI.value,
            "confidence": 0.7,
            "entities": self._extract_entities(message),
            "sub_intents": [
                {"type": intent.value, "confidence": 0.7}
                for intent in detected_intents
            ]
        }
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract entities from message using simple patterns.
        """
        import re
        from datetime import datetime, timedelta
        
        entities = {}
        
        # Date patterns
        today_patterns = ["today", "tonight"]
        tomorrow_patterns = ["tomorrow"]
        
        message_lower = message.lower()
        
        if any(p in message_lower for p in today_patterns):
            entities["date"] = datetime.now().strftime("%Y-%m-%d")
        elif any(p in message_lower for p in tomorrow_patterns):
            entities["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Time patterns
        time_pattern = r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)\b'
        time_matches = re.findall(time_pattern, message)
        if time_matches:
            entities["time"] = time_matches[0]
        
        # Location patterns (after "to" or "at")
        to_pattern = r'\bto\s+([A-Z][a-zA-Z\s]+?)(?:\.|,|$|\s+and|\s+then)'
        to_matches = re.findall(to_pattern, message)
        if to_matches:
            entities["destination"] = to_matches[0].strip()
        
        at_pattern = r'\bat\s+([A-Z][a-zA-Z\s]+?)(?:\.|,|$|\s+and|\s+then)'
        at_matches = re.findall(at_pattern, message)
        if at_matches:
            entities["location"] = at_matches[0].strip()
        
        return entities
    
    async def create_execution_plan(
        self,
        intent: Dict[str, Any],
        previous_results: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Create an execution plan based on the analyzed intent.
        
        Args:
            intent: Analyzed intent
            previous_results: Results from previous agent executions
            
        Returns:
            List of tasks to execute
        """
        previous_results = previous_results or {}
        tasks = []
        
        intent_type = intent.get("type")
        entities = intent.get("entities", {})
        sub_intents = intent.get("sub_intents", [])
        
        if intent_type == IntentType.MULTI.value:
            # Handle multiple intents
            for i, sub_intent in enumerate(sub_intents):
                sub_tasks = await self._create_tasks_for_intent(
                    sub_intent.get("type"),
                    entities,
                    f"task_{i}_"
                )
                tasks.extend(sub_tasks)
        else:
            tasks = await self._create_tasks_for_intent(
                intent_type,
                entities,
                "task_"
            )
        
        # Add dependencies between tasks
        tasks = self._add_dependencies(tasks)
        
        return tasks
    
    async def _create_tasks_for_intent(
        self,
        intent_type: str,
        entities: Dict[str, Any],
        prefix: str
    ) -> List[Dict[str, Any]]:
        """
        Create tasks for a specific intent type.
        """
        tasks = []
        
        if intent_type == IntentType.TRANSPORT.value:
            tasks.append({
                "id": f"{prefix}transport_estimate",
                "type": "get_ride_estimate",
                "agent": "transport",
                "parameters": {
                    "destination": entities.get("destination"),
                    "pickup_time": entities.get("time")
                },
                "dependencies": []
            })
            tasks.append({
                "id": f"{prefix}transport_book",
                "type": "book_ride",
                "agent": "transport",
                "parameters": {
                    "destination": entities.get("destination")
                },
                "dependencies": [f"{prefix}transport_estimate"]
            })
        
        elif intent_type == IntentType.CALENDAR.value:
            tasks.append({
                "id": f"{prefix}calendar_check",
                "type": "check_availability",
                "agent": "calendar",
                "parameters": {
                    "date": entities.get("date")
                },
                "dependencies": []
            })
        
        elif intent_type == IntentType.MEDICAL.value:
            tasks.append({
                "id": f"{prefix}medical_search",
                "type": "find_doctor",
                "agent": "medical",
                "parameters": {
                    "specialty": entities.get("specialty"),
                    "date": entities.get("date")
                },
                "dependencies": []
            })
            tasks.append({
                "id": f"{prefix}medical_book",
                "type": "book_appointment",
                "agent": "medical",
                "parameters": {},
                "dependencies": [f"{prefix}medical_search"]
            })
        
        elif intent_type == IntentType.MOVIE.value:
            tasks.append({
                "id": f"{prefix}movie_search",
                "type": "search_movies",
                "agent": "movie",
                "parameters": {
                    "query": entities.get("movie_name"),
                    "date": entities.get("date")
                },
                "dependencies": []
            })
        
        elif intent_type == IntentType.REMINDER.value:
            tasks.append({
                "id": f"{prefix}reminder_create",
                "type": "create_reminder",
                "agent": "reminder",
                "parameters": {
                    "time": entities.get("time"),
                    "date": entities.get("date")
                },
                "dependencies": []
            })
        
        return tasks
    
    def _add_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add logical dependencies between tasks.
        """
        # Example: Calendar check should complete before booking transport
        task_types = {t["type"]: t for t in tasks}
        
        if "book_ride" in task_types and "check_availability" in task_types:
            calendar_task = task_types["check_availability"]
            transport_task = task_types["book_ride"]
            
            if calendar_task["id"] not in transport_task["dependencies"]:
                transport_task["dependencies"].append(calendar_task["id"])
        
        return tasks
    
    async def generate_response(
        self,
        intent: Dict[str, Any],
        results: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a user-friendly response from agent results.
        
        Args:
            intent: Original intent
            results: Results from agent executions
            actions: Pending actions
            
        Returns:
            Natural language response
        """
        if not results:
            return "I couldn't find any relevant information for your request."
        
        # Build response based on results
        response_parts = []
        
        for task_id, result in results.items():
            if result.get("success"):
                data = result.get("data", {})
                summary = data.get("summary", "")
                if summary:
                    response_parts.append(summary)
            else:
                error = result.get("error", "Unknown error")
                response_parts.append(f"I encountered an issue: {error}")
        
        # Add action summaries
        if actions:
            action_summary = self._summarize_actions(actions)
            response_parts.append(action_summary)
        
        return " ".join(response_parts) if response_parts else "I've processed your request."
    
    async def generate_confirmation_request(
        self,
        actions: List[Dict[str, Any]],
        results: Dict[str, Any]
    ) -> str:
        """
        Generate a confirmation request for pending actions.
        """
        if not actions:
            return "No actions require confirmation."
        
        parts = ["I've found the following options:\n"]
        
        for action in actions:
            action_type = action.get("type", "action")
            details = action.get("details", {})
            
            if action_type == "ride_booking":
                parts.append(
                    f"🚗 **Ride**: {details.get('ride_type', 'UberX')} to "
                    f"{details.get('destination', 'destination')}\n"
                    f"   Price: ${details.get('price', '?')}\n"
                    f"   ETA: {details.get('eta', '?')} minutes"
                )
            elif action_type == "appointment":
                parts.append(
                    f"🏥 **Appointment**: {details.get('doctor', 'Doctor')}\n"
                    f"   Time: {details.get('time', 'TBD')}\n"
                    f"   Location: {details.get('location', 'TBD')}"
                )
            else:
                parts.append(f"📋 **{action_type}**: {details}")
        
        parts.append("\nWould you like me to proceed?")
        
        return "\n".join(parts)
    
    def _summarize_actions(self, actions: List[Dict[str, Any]]) -> str:
        """Create a summary of pending actions."""
        if not actions:
            return ""
        
        count = len(actions)
        if count == 1:
            return "I have 1 action ready for your confirmation."
        return f"I have {count} actions ready for your confirmation."
]]>
