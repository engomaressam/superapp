<![CDATA["""
Transport API Routes
Direct access to ride booking operations.
"""

from typing import Optional, List
from datetime import datetime
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Location(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = None


class EstimateRequest(BaseModel):
    pickup: Location
    dropoff: Location
    ride_types: List[str] = ["UberX", "UberXL", "UberBlack"]


class BookRequest(BaseModel):
    pickup: Location
    dropoff: Location
    ride_type: str = "UberX"
    scheduled_time: Optional[str] = None
    payment_method: Optional[str] = None


@router.post("/estimate")
async def get_estimate(request: EstimateRequest):
    """
    Get price and time estimates for a ride.
    """
    estimates = []
    
    base_prices = {
        "UberX": (10, 15),
        "UberXL": (18, 25),
        "UberBlack": (30, 45)
    }
    
    for ride_type in request.ride_types:
        if ride_type in base_prices:
            min_p, max_p = base_prices[ride_type]
            estimates.append({
                "ride_type": ride_type,
                "price": {
                    "min": min_p,
                    "max": max_p,
                    "currency": "USD"
                },
                "duration_minutes": 25,
                "distance_km": 18.5,
                "surge_multiplier": 1.0
            })
    
    return {
        "estimates": estimates,
        "pickup_eta_minutes": 8
    }


@router.post("/book")
async def book_ride(request: BookRequest):
    """
    Book a ride.
    """
    ride_id = f"ride_{uuid.uuid4().hex[:12]}"
    
    return {
        "ride_id": ride_id,
        "status": "confirmed",
        "ride_type": request.ride_type,
        "pickup": request.pickup.dict(),
        "dropoff": request.dropoff.dict(),
        "driver": {
            "name": "Ahmed M.",
            "rating": 4.9,
            "vehicle": {
                "make": "Toyota",
                "model": "Corolla",
                "color": "White",
                "plate": "ABC 123"
            },
            "phone": "+20123456789"
        },
        "eta_minutes": 8,
        "price": {
            "estimated": 12.50,
            "currency": "USD"
        },
        "scheduled_time": request.scheduled_time,
        "tracking_url": f"https://m.uber.com/track/{ride_id}"
    }


@router.get("/ride/{ride_id}")
async def get_ride_status(ride_id: str):
    """
    Get current status of a ride.
    """
    return {
        "ride_id": ride_id,
        "status": "driver_en_route",
        "driver": {
            "name": "Ahmed M.",
            "rating": 4.9,
            "location": {
                "lat": 30.0500,
                "lng": 31.2400
            }
        },
        "eta_minutes": 5
    }


@router.delete("/ride/{ride_id}")
async def cancel_ride(ride_id: str):
    """
    Cancel a ride.
    """
    return {
        "ride_id": ride_id,
        "status": "cancelled",
        "cancellation_fee": 0.0,
        "message": "Ride cancelled successfully"
    }
]]>
