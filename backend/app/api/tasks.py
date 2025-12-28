<![CDATA["""
Tasks API Routes
Track and manage active tasks.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# Models
class TaskStep(BaseModel):
    name: str
    status: str
    result: Optional[Dict[str, Any]] = None


class TaskProgress(BaseModel):
    current_step: str
    total_steps: int
    percentage: int


class TaskResponse(BaseModel):
    id: str
    type: str
    status: str
    created_at: str
    updated_at: str
    summary: str
    progress: TaskProgress
    metadata: Dict[str, Any]


class TaskDetailResponse(TaskResponse):
    agent: str
    steps: List[TaskStep]
    timeline: List[Dict[str, Any]]


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int


# In-memory task store (use database in production)
active_tasks: Dict[str, Dict[str, Any]] = {
    "task_001": {
        "id": "task_001",
        "type": "ride_booking",
        "status": "in_progress",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:32:00Z",
        "summary": "Uber to Cairo Festival City",
        "agent": "TransportAgent",
        "progress": {
            "current_step": "driver_en_route",
            "total_steps": 4,
            "percentage": 50
        },
        "metadata": {
            "ride_id": "ride_uber_12345",
            "eta": "6 minutes"
        },
        "steps": [
            {"name": "get_estimate", "status": "completed", "result": {"price": 12.50}},
            {"name": "request_ride", "status": "completed", "result": {"ride_id": "ride_uber_12345"}},
            {"name": "await_pickup", "status": "in_progress", "result": None},
            {"name": "complete_ride", "status": "pending", "result": None}
        ],
        "timeline": [
            {"event": "task_created", "timestamp": "2024-01-15T10:30:00Z"},
            {"event": "estimate_received", "timestamp": "2024-01-15T10:30:15Z", "data": {"price": 12.50}},
            {"event": "ride_requested", "timestamp": "2024-01-15T10:31:00Z"},
            {"event": "driver_assigned", "timestamp": "2024-01-15T10:32:00Z", "data": {"driver": "Ahmed M."}}
        ]
    }
}


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by task type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get all active tasks for the current user.
    """
    # Filter tasks
    filtered = list(active_tasks.values())
    
    if status:
        filtered = [t for t in filtered if t["status"] == status]
    
    if type:
        filtered = [t for t in filtered if t["type"] == type]
    
    # Paginate
    total = len(filtered)
    filtered = filtered[offset:offset + limit]
    
    return TaskListResponse(
        tasks=[
            TaskResponse(
                id=t["id"],
                type=t["type"],
                status=t["status"],
                created_at=t["created_at"],
                updated_at=t["updated_at"],
                summary=t["summary"],
                progress=TaskProgress(**t["progress"]),
                metadata=t["metadata"]
            )
            for t in filtered
        ],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(task_id: str):
    """
    Get detailed information about a specific task.
    """
    if task_id not in active_tasks:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "TASK_NOT_FOUND",
                "message": f"Task {task_id} not found"
            }
        )
    
    task = active_tasks[task_id]
    
    return TaskDetailResponse(
        id=task["id"],
        type=task["type"],
        status=task["status"],
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        summary=task["summary"],
        progress=TaskProgress(**task["progress"]),
        metadata=task["metadata"],
        agent=task["agent"],
        steps=[TaskStep(**s) for s in task["steps"]],
        timeline=task["timeline"]
    )


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str, reason: Optional[str] = None):
    """
    Cancel an active task.
    """
    if task_id not in active_tasks:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "TASK_NOT_FOUND",
                "message": f"Task {task_id} not found"
            }
        )
    
    task = active_tasks[task_id]
    
    if task["status"] == "completed":
        raise HTTPException(
            status_code=400,
            detail={
                "code": "CANNOT_CANCEL",
                "message": "Cannot cancel a completed task"
            }
        )
    
    # Update task status
    task["status"] = "cancelled"
    task["updated_at"] = datetime.utcnow().isoformat() + "Z"
    task["timeline"].append({
        "event": "task_cancelled",
        "timestamp": task["updated_at"],
        "data": {"reason": reason}
    })
    
    return {
        "task_id": task_id,
        "status": "cancelled",
        "message": "Task cancelled successfully"
    }


@router.post("/{task_id}/retry")
async def retry_task(task_id: str):
    """
    Retry a failed task.
    """
    if task_id not in active_tasks:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "TASK_NOT_FOUND",
                "message": f"Task {task_id} not found"
            }
        )
    
    task = active_tasks[task_id]
    
    if task["status"] != "failed":
        raise HTTPException(
            status_code=400,
            detail={
                "code": "CANNOT_RETRY",
                "message": "Can only retry failed tasks"
            }
        )
    
    # Reset task status
    task["status"] = "pending"
    task["updated_at"] = datetime.utcnow().isoformat() + "Z"
    task["timeline"].append({
        "event": "task_retried",
        "timestamp": task["updated_at"]
    })
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Task queued for retry"
    }
]]>
