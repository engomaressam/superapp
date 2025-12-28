<![CDATA["""
Chat API Routes
Main interface for user interactions with ARIA.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.agents.orchestrator import get_orchestrator

router = APIRouter()


# Request/Response Models
class Location(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = None


class ChatContext(BaseModel):
    location: Optional[Location] = None
    timezone: str = "UTC"


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    context: Optional[ChatContext] = None


class ActionDetails(BaseModel):
    id: str
    type: str
    status: str
    details: Dict[str, Any]


class ChatMessageResponse(BaseModel):
    response_id: str
    conversation_id: str
    message: str
    actions: List[ActionDetails] = []
    suggested_responses: List[str] = []
    requires_confirmation: bool = False


class ActionConfirmRequest(BaseModel):
    confirmed: bool
    modifications: Optional[Dict[str, Any]] = None


class ActionConfirmResponse(BaseModel):
    action_id: str
    status: str
    result: Optional[Dict[str, Any]] = None


# In-memory conversation store (use Redis in production)
conversations: Dict[str, List[Dict[str, Any]]] = {}
pending_actions: Dict[str, Dict[str, Any]] = {}


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Send a message to ARIA and receive an AI-powered response.
    
    The orchestrator will:
    1. Parse the user's intent
    2. Create an execution plan
    3. Route to appropriate agents
    4. Return results and any pending actions
    """
    # Generate IDs
    response_id = f"resp_{uuid.uuid4().hex[:12]}"
    conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:12]}"
    
    # Get orchestrator
    orchestrator = get_orchestrator()
    
    # Build context
    context = {}
    if request.context:
        if request.context.location:
            context["location"] = {
                "lat": request.context.location.lat,
                "lng": request.context.location.lng,
                "address": request.context.location.address
            }
        context["timezone"] = request.context.timezone
    
    try:
        # Process through orchestrator
        result = await orchestrator.process(
            user_message=request.message,
            user_id="demo_user",  # In production, from auth
            conversation_id=conversation_id,
            context=context
        )
        
        # Store conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        conversations[conversation_id].append({
            "role": "assistant",
            "content": result.get("response", ""),
            "timestamp": datetime.now().isoformat()
        })
        
        # Store pending actions
        actions = []
        for action in result.get("actions", []):
            action_id = action.get("id", f"action_{uuid.uuid4().hex[:8]}")
            pending_actions[action_id] = action
            actions.append(ActionDetails(
                id=action_id,
                type=action.get("type", "unknown"),
                status=action.get("status", "pending"),
                details=action.get("details", {})
            ))
        
        # Generate suggested responses
        suggested = _generate_suggestions(result)
        
        return ChatMessageResponse(
            response_id=response_id,
            conversation_id=conversation_id,
            message=result.get("response", "I'm processing your request."),
            actions=actions,
            suggested_responses=suggested,
            requires_confirmation=result.get("requires_confirmation", False)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PROCESSING_ERROR",
                "message": str(e)
            }
        )


@router.post("/action/{action_id}/confirm", response_model=ActionConfirmResponse)
async def confirm_action(action_id: str, request: ActionConfirmRequest):
    """
    Confirm or reject a pending action.
    """
    if action_id not in pending_actions:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "ACTION_NOT_FOUND",
                "message": f"Action {action_id} not found or expired"
            }
        )
    
    action = pending_actions[action_id]
    
    if not request.confirmed:
        # User rejected
        del pending_actions[action_id]
        return ActionConfirmResponse(
            action_id=action_id,
            status="rejected",
            result={"message": "Action cancelled by user"}
        )
    
    # Execute the confirmed action
    try:
        # In production, this would trigger actual execution
        result = await _execute_confirmed_action(action, request.modifications)
        
        # Remove from pending
        del pending_actions[action_id]
        
        return ActionConfirmResponse(
            action_id=action_id,
            status="executed",
            result=result
        )
        
    except Exception as e:
        return ActionConfirmResponse(
            action_id=action_id,
            status="failed",
            result={"error": str(e)}
        )


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation history.
    """
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CONVERSATION_NOT_FOUND",
                "message": f"Conversation {conversation_id} not found"
            }
        )
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }


# WebSocket for real-time updates
class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for real-time updates.
    """
    user_id = "demo_user"  # In production, validate token
    
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            msg_type = data.get("type")
            
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif msg_type == "message":
                # Process message through orchestrator
                orchestrator = get_orchestrator()
                result = await orchestrator.process(
                    user_message=data.get("content", ""),
                    user_id=user_id,
                    conversation_id=data.get("conversation_id", "default"),
                    context=data.get("context", {})
                )
                
                await websocket.send_json({
                    "type": "response",
                    "data": result
                })
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)


def _generate_suggestions(result: Dict[str, Any]) -> List[str]:
    """Generate contextual response suggestions."""
    suggestions = []
    
    actions = result.get("actions", [])
    
    if result.get("requires_confirmation"):
        suggestions.extend(["Yes, proceed", "No, cancel", "Show more options"])
    elif actions:
        suggestions.extend(["Confirm all", "Cancel"])
    else:
        suggestions.extend(["Tell me more", "What else can you do?"])
    
    return suggestions[:3]


async def _execute_confirmed_action(
    action: Dict[str, Any],
    modifications: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Execute a confirmed action."""
    action_type = action.get("type")
    details = action.get("details", {})
    
    # Apply any modifications
    if modifications:
        details.update(modifications)
    
    # Mock execution results
    if action_type == "ride_booking":
        return {
            "success": True,
            "ride_id": f"ride_{uuid.uuid4().hex[:8]}",
            "driver": {
                "name": "Ahmed M.",
                "rating": 4.9,
                "vehicle": "Toyota Corolla (White)",
                "plate": "ABC 123"
            },
            "eta_minutes": 8,
            "tracking_url": "https://m.uber.com/track/..."
        }
    
    elif action_type == "appointment":
        return {
            "success": True,
            "appointment_id": f"apt_{uuid.uuid4().hex[:8]}",
            "confirmation": "Your appointment has been booked",
            "details": details
        }
    
    return {
        "success": True,
        "message": "Action executed successfully",
        "details": details
    }
]]>
