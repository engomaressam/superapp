<![CDATA[# 📚 API Reference

## Base URL

```
Production: https://api.aria-agent.com/v1
Development: http://localhost:8000/v1
```

## Authentication

All API requests require authentication via Bearer token:

```http
Authorization: Bearer <your-api-key>
```

---

## Endpoints

### Chat

#### Send Message

Send a message to ARIA and receive an AI-powered response with potential actions.

```http
POST /chat/message
```

**Request Body:**

```json
{
  "message": "Book me an Uber to Cairo Festival City",
  "conversation_id": "conv_abc123",  // Optional, for context continuity
  "context": {
    "location": {
      "lat": 30.0444,
      "lng": 31.2357
    }
  }
}
```

**Response:**

```json
{
  "response_id": "resp_xyz789",
  "conversation_id": "conv_abc123",
  "message": "I found a ride for you. UberX to Cairo Festival City: $12.50, arriving in 8 minutes. Should I book it?",
  "actions": [
    {
      "id": "action_001",
      "type": "ride_booking",
      "status": "pending_confirmation",
      "details": {
        "service": "uber",
        "ride_type": "UberX",
        "pickup": "Current Location",
        "dropoff": "Cairo Festival City",
        "estimated_price": 12.50,
        "estimated_arrival": "8 minutes",
        "currency": "USD"
      }
    }
  ],
  "suggested_responses": [
    "Yes, book it",
    "Show me other options",
    "Cancel"
  ]
}
```

#### Confirm Action

Confirm or reject a pending action.

```http
POST /chat/action/{action_id}/confirm
```

**Request Body:**

```json
{
  "confirmed": true,
  "modifications": {}  // Optional modifications
}
```

**Response:**

```json
{
  "action_id": "action_001",
  "status": "confirmed",
  "result": {
    "ride_id": "ride_uber_12345",
    "driver": {
      "name": "Ahmed M.",
      "rating": 4.9,
      "vehicle": "Toyota Corolla (White)",
      "plate": "ABC 123"
    },
    "eta": "8 minutes",
    "tracking_url": "https://m.uber.com/track/..."
  }
}
```

---

### Tasks

#### Get Active Tasks

Get all active tasks for the current user.

```http
GET /tasks
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (pending, in_progress, completed, failed) |
| type | string | Filter by task type |
| limit | int | Max results (default: 20) |
| offset | int | Pagination offset |

**Response:**

```json
{
  "tasks": [
    {
      "id": "task_001",
      "type": "ride_booking",
      "status": "in_progress",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:32:00Z",
      "summary": "Uber to Cairo Festival City",
      "progress": {
        "current_step": "driver_en_route",
        "total_steps": 4,
        "percentage": 50
      },
      "metadata": {
        "ride_id": "ride_uber_12345",
        "eta": "6 minutes"
      }
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### Get Task Details

```http
GET /tasks/{task_id}
```

**Response:**

```json
{
  "id": "task_001",
  "type": "ride_booking",
  "status": "in_progress",
  "created_at": "2024-01-15T10:30:00Z",
  "agent": "TransportAgent",
  "steps": [
    {
      "name": "get_estimate",
      "status": "completed",
      "result": {"price": 12.50}
    },
    {
      "name": "request_ride",
      "status": "completed",
      "result": {"ride_id": "ride_uber_12345"}
    },
    {
      "name": "await_pickup",
      "status": "in_progress",
      "result": null
    },
    {
      "name": "complete_ride",
      "status": "pending",
      "result": null
    }
  ],
  "timeline": [
    {
      "event": "task_created",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "event": "estimate_received",
      "timestamp": "2024-01-15T10:30:15Z",
      "data": {"price": 12.50}
    },
    {
      "event": "ride_requested",
      "timestamp": "2024-01-15T10:31:00Z"
    },
    {
      "event": "driver_assigned",
      "timestamp": "2024-01-15T10:32:00Z",
      "data": {"driver": "Ahmed M."}
    }
  ]
}
```

#### Cancel Task

```http
POST /tasks/{task_id}/cancel
```

**Request Body:**

```json
{
  "reason": "Changed my mind"
}
```

---

### Calendar

#### Get Events

```http
GET /calendar/events
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | ISO 8601 date (required) |
| end_date | string | ISO 8601 date (required) |
| calendar_id | string | Specific calendar (optional) |

**Response:**

```json
{
  "events": [
    {
      "id": "evt_001",
      "title": "Team Meeting",
      "start": "2024-01-15T10:00:00Z",
      "end": "2024-01-15T11:00:00Z",
      "location": "Office",
      "calendar": "Work",
      "attendees": ["john@example.com"],
      "reminders": [{"minutes": 30, "method": "popup"}]
    }
  ]
}
```

#### Create Event

```http
POST /calendar/events
```

**Request Body:**

```json
{
  "title": "Doctor Appointment",
  "start": "2024-01-16T14:00:00Z",
  "end": "2024-01-16T15:00:00Z",
  "location": "Medical Center, Nasr City",
  "description": "Dermatologist - Dr. Sarah",
  "reminders": [
    {"minutes": 60, "method": "push"},
    {"minutes": 30, "method": "sms"}
  ]
}
```

#### Check Availability

```http
POST /calendar/availability
```

**Request Body:**

```json
{
  "date": "2024-01-16",
  "duration_minutes": 60,
  "preferred_times": ["morning", "afternoon"]
}
```

**Response:**

```json
{
  "available_slots": [
    {
      "start": "2024-01-16T09:00:00Z",
      "end": "2024-01-16T10:00:00Z",
      "preference_match": "morning"
    },
    {
      "start": "2024-01-16T14:00:00Z",
      "end": "2024-01-16T15:00:00Z",
      "preference_match": "afternoon"
    }
  ],
  "conflicts": [
    {
      "time": "2024-01-16T11:00:00Z",
      "event": "Lunch with Ahmed"
    }
  ]
}
```

---

### Transport

#### Get Ride Estimate

```http
POST /transport/estimate
```

**Request Body:**

```json
{
  "pickup": {
    "lat": 30.0444,
    "lng": 31.2357,
    "address": "Tahrir Square, Cairo"
  },
  "dropoff": {
    "lat": 30.0131,
    "lng": 31.4089,
    "address": "Cairo Festival City"
  },
  "ride_types": ["UberX", "UberXL", "UberBlack"]
}
```

**Response:**

```json
{
  "estimates": [
    {
      "ride_type": "UberX",
      "price": {
        "min": 11.00,
        "max": 14.00,
        "currency": "USD"
      },
      "duration_minutes": 25,
      "distance_km": 18.5,
      "surge_multiplier": 1.0
    },
    {
      "ride_type": "UberXL",
      "price": {
        "min": 18.00,
        "max": 22.00,
        "currency": "USD"
      },
      "duration_minutes": 25,
      "distance_km": 18.5,
      "surge_multiplier": 1.0
    }
  ],
  "pickup_eta_minutes": 8
}
```

#### Book Ride

```http
POST /transport/book
```

**Request Body:**

```json
{
  "pickup": {
    "lat": 30.0444,
    "lng": 31.2357
  },
  "dropoff": {
    "lat": 30.0131,
    "lng": 31.4089
  },
  "ride_type": "UberX",
  "scheduled_time": null,  // null for immediate, ISO 8601 for scheduled
  "payment_method": "card_ending_4242"
}
```

---

### Medical

#### Search Doctors

```http
POST /medical/search
```

**Request Body:**

```json
{
  "specialty": "dermatologist",
  "location": "Nasr City, Cairo",
  "insurance": "AXA",
  "date": "2024-01-16",
  "sort_by": "rating"  // rating, price, availability
}
```

**Response:**

```json
{
  "doctors": [
    {
      "id": "doc_001",
      "name": "Dr. Sarah Ahmed",
      "specialty": "Dermatologist",
      "clinic": "Skin Care Center",
      "address": "15 Makram Ebeid St, Nasr City",
      "rating": 4.8,
      "reviews_count": 234,
      "consultation_fee": 300,
      "currency": "EGP",
      "available_slots": [
        "2024-01-16T10:00:00",
        "2024-01-16T14:30:00",
        "2024-01-16T16:00:00"
      ],
      "accepts_insurance": ["AXA", "Bupa"],
      "profile_url": "https://vezeeta.com/dr/sarah-ahmed"
    }
  ],
  "total": 15,
  "source": "vezeeta"
}
```

#### Book Appointment

```http
POST /medical/book
```

**Request Body:**

```json
{
  "doctor_id": "doc_001",
  "slot": "2024-01-16T14:30:00",
  "patient_info": {
    "name": "John Doe",
    "phone": "+20123456789",
    "reason": "Skin consultation"
  }
}
```

---

### Reminders

#### Create Reminder

```http
POST /reminders
```

**Request Body:**

```json
{
  "message": "Take medication",
  "trigger_time": "2024-01-15T20:00:00Z",
  "repeat": {
    "frequency": "daily",
    "until": "2024-02-15"
  },
  "notification_methods": ["push", "sms"]
}
```

#### List Reminders

```http
GET /reminders
```

---

### Movies

#### Search Movies

```http
GET /movies/search
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| query | string | Search term |
| genre | string | Filter by genre |
| now_playing | bool | Only movies in theaters |

#### Get Showtimes

```http
POST /movies/showtimes
```

**Request Body:**

```json
{
  "movie_id": "movie_dune2",
  "location": {
    "lat": 30.0444,
    "lng": 31.2357
  },
  "date": "2024-01-15",
  "radius_km": 15
}
```

**Response:**

```json
{
  "movie": {
    "id": "movie_dune2",
    "title": "Dune: Part Two",
    "rating": 8.5,
    "runtime_minutes": 166
  },
  "theaters": [
    {
      "name": "VOX Cinemas - City Stars",
      "address": "City Stars Mall, Nasr City",
      "distance_km": 5.2,
      "showtimes": [
        {
          "time": "2024-01-15T18:00:00",
          "format": "IMAX",
          "language": "English",
          "subtitles": "Arabic",
          "available_seats": 45
        },
        {
          "time": "2024-01-15T21:30:00",
          "format": "Standard",
          "language": "English",
          "subtitles": "Arabic",
          "available_seats": 120
        }
      ]
    }
  ]
}
```

---

## WebSocket API

For real-time updates, connect to the WebSocket endpoint:

```
wss://api.aria-agent.com/v1/ws?token=<your-token>
```

### Event Types

```json
// Task status update
{
  "type": "task_update",
  "task_id": "task_001",
  "status": "completed",
  "data": {...}
}

// Chat message
{
  "type": "message",
  "conversation_id": "conv_abc123",
  "content": "Your ride has arrived!",
  "timestamp": "2024-01-15T10:40:00Z"
}

// Action required
{
  "type": "action_required",
  "action_id": "action_002",
  "message": "Please confirm the booking",
  "expires_at": "2024-01-15T10:45:00Z"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The pickup location is required",
    "details": {
      "field": "pickup",
      "reason": "missing"
    }
  },
  "request_id": "req_abc123"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_REQUEST | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Invalid or missing auth token |
| FORBIDDEN | 403 | Not authorized for this action |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMITED | 429 | Too many requests |
| AGENT_ERROR | 500 | Agent execution failed |
| SERVICE_UNAVAILABLE | 503 | External service unavailable |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| /chat/* | 60 requests/minute |
| /tasks/* | 100 requests/minute |
| /calendar/* | 100 requests/minute |
| /transport/* | 30 requests/minute |
| /medical/* | 20 requests/minute |

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705320000
```
]]>
