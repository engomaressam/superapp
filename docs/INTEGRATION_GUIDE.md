<![CDATA[# 🔌 Integration Guide

This guide explains how to integrate ARIA with external services across all three tiers.

---

## Tier 1: Direct API Integrations

### Uber Integration

#### Prerequisites
1. Register at [Uber Developer Portal](https://developer.uber.com)
2. Create an application
3. Obtain OAuth credentials

#### Setup

```python
# backend/app/tools/uber_api.py

from dataclasses import dataclass
from typing import Optional
import httpx

@dataclass
class Location:
    latitude: float
    longitude: float
    address: Optional[str] = None

@dataclass
class RideEstimate:
    ride_type: str
    price_min: float
    price_max: float
    currency: str
    duration_minutes: int
    distance_km: float

@dataclass
class RideRequest:
    ride_id: str
    status: str
    driver_name: Optional[str]
    driver_rating: Optional[float]
    vehicle: Optional[str]
    eta_minutes: int

class UberAPI:
    """
    Uber Riders API integration.
    
    Documentation: https://developer.uber.com/docs/riders/introduction
    """
    
    BASE_URL = "https://api.uber.com/v1.2"
    
    def __init__(self, client_id: str, client_secret: str, server_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.server_token = server_token
        self._access_token: Optional[str] = None
    
    async def get_estimate(
        self,
        pickup: Location,
        dropoff: Location,
        ride_types: list[str] = ["uberX"]
    ) -> list[RideEstimate]:
        """
        Get price estimates for a ride.
        
        Args:
            pickup: Pickup location
            dropoff: Dropoff location
            ride_types: List of ride types to get estimates for
            
        Returns:
            List of RideEstimate objects
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/estimates/price",
                headers={"Authorization": f"Token {self.server_token}"},
                params={
                    "start_latitude": pickup.latitude,
                    "start_longitude": pickup.longitude,
                    "end_latitude": dropoff.latitude,
                    "end_longitude": dropoff.longitude,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            estimates = []
            for price in data.get("prices", []):
                if price["display_name"].lower() in [rt.lower() for rt in ride_types]:
                    estimates.append(RideEstimate(
                        ride_type=price["display_name"],
                        price_min=price["low_estimate"],
                        price_max=price["high_estimate"],
                        currency=price["currency_code"],
                        duration_minutes=price["duration"] // 60,
                        distance_km=price["distance"] * 1.60934  # miles to km
                    ))
            
            return estimates
    
    async def request_ride(
        self,
        pickup: Location,
        dropoff: Location,
        ride_type: str = "uberX",
        user_access_token: str = None
    ) -> RideRequest:
        """
        Request a ride (requires user OAuth token).
        
        Note: This requires the user to have authorized the app
        via OAuth 2.0 flow.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/requests",
                headers={"Authorization": f"Bearer {user_access_token}"},
                json={
                    "start_latitude": pickup.latitude,
                    "start_longitude": pickup.longitude,
                    "end_latitude": dropoff.latitude,
                    "end_longitude": dropoff.longitude,
                    "product_id": await self._get_product_id(ride_type, pickup)
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return RideRequest(
                ride_id=data["request_id"],
                status=data["status"],
                driver_name=data.get("driver", {}).get("name"),
                driver_rating=data.get("driver", {}).get("rating"),
                vehicle=data.get("vehicle", {}).get("make"),
                eta_minutes=data.get("eta", 0)
            )
    
    async def get_ride_status(self, ride_id: str, user_access_token: str) -> dict:
        """Get current status of a ride."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/requests/{ride_id}",
                headers={"Authorization": f"Bearer {user_access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def cancel_ride(self, ride_id: str, user_access_token: str) -> bool:
        """Cancel a ride request."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.BASE_URL}/requests/{ride_id}",
                headers={"Authorization": f"Bearer {user_access_token}"}
            )
            return response.status_code == 204
```

### Google Calendar Integration

```python
# backend/app/tools/google_calendar.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class CalendarEvent:
    id: str
    title: str
    start: datetime
    end: datetime
    location: Optional[str]
    description: Optional[str]
    attendees: List[str]

class GoogleCalendarAPI:
    """
    Google Calendar API integration.
    
    Setup:
    1. Create project in Google Cloud Console
    2. Enable Calendar API
    3. Create OAuth 2.0 credentials
    4. Download credentials.json
    """
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials: Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    async def get_events(
        self,
        start_date: datetime,
        end_date: datetime,
        calendar_id: str = 'primary'
    ) -> List[CalendarEvent]:
        """
        Get events within a date range.
        """
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = []
        for item in events_result.get('items', []):
            events.append(CalendarEvent(
                id=item['id'],
                title=item.get('summary', 'Untitled'),
                start=datetime.fromisoformat(
                    item['start'].get('dateTime', item['start'].get('date'))
                ),
                end=datetime.fromisoformat(
                    item['end'].get('dateTime', item['end'].get('date'))
                ),
                location=item.get('location'),
                description=item.get('description'),
                attendees=[
                    a['email'] for a in item.get('attendees', [])
                ]
            ))
        
        return events
    
    async def create_event(
        self,
        title: str,
        start: datetime,
        end: datetime,
        location: Optional[str] = None,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminders: Optional[List[dict]] = None,
        calendar_id: str = 'primary'
    ) -> CalendarEvent:
        """
        Create a new calendar event.
        """
        event_body = {
            'summary': title,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        if location:
            event_body['location'] = location
        if description:
            event_body['description'] = description
        if attendees:
            event_body['attendees'] = [{'email': email} for email in attendees]
        if reminders:
            event_body['reminders'] = {
                'useDefault': False,
                'overrides': reminders
            }
        
        created = self.service.events().insert(
            calendarId=calendar_id,
            body=event_body
        ).execute()
        
        return CalendarEvent(
            id=created['id'],
            title=title,
            start=start,
            end=end,
            location=location,
            description=description,
            attendees=attendees or []
        )
    
    async def check_conflicts(
        self,
        proposed_start: datetime,
        proposed_end: datetime,
        calendar_id: str = 'primary'
    ) -> List[CalendarEvent]:
        """
        Check for conflicting events.
        """
        events = await self.get_events(
            proposed_start - timedelta(hours=1),
            proposed_end + timedelta(hours=1),
            calendar_id
        )
        
        conflicts = []
        for event in events:
            # Check for overlap
            if (event.start < proposed_end and event.end > proposed_start):
                conflicts.append(event)
        
        return conflicts
    
    async def find_free_slots(
        self,
        date: datetime,
        duration_minutes: int,
        working_hours: tuple = (9, 18),
        calendar_id: str = 'primary'
    ) -> List[tuple]:
        """
        Find available time slots on a given date.
        
        Returns list of (start, end) tuples.
        """
        start_of_day = date.replace(hour=working_hours[0], minute=0, second=0)
        end_of_day = date.replace(hour=working_hours[1], minute=0, second=0)
        
        events = await self.get_events(start_of_day, end_of_day, calendar_id)
        
        # Sort events by start time
        events.sort(key=lambda e: e.start)
        
        free_slots = []
        current_time = start_of_day
        
        for event in events:
            # Check if there's a gap before this event
            gap = (event.start - current_time).total_seconds() / 60
            if gap >= duration_minutes:
                free_slots.append((current_time, event.start))
            
            # Move current time to end of this event
            current_time = max(current_time, event.end)
        
        # Check for slot after last event
        gap = (end_of_day - current_time).total_seconds() / 60
        if gap >= duration_minutes:
            free_slots.append((current_time, end_of_day))
        
        return free_slots
```

### TMDB (Movie Database) Integration

```python
# backend/app/tools/tmdb_api.py

import httpx
from dataclasses import dataclass
from typing import List, Optional
from datetime import date

@dataclass
class Movie:
    id: int
    title: str
    overview: str
    release_date: date
    rating: float
    poster_url: Optional[str]
    genres: List[str]
    runtime_minutes: Optional[int]

class TMDBApi:
    """
    The Movie Database API integration.
    
    Get API key at: https://www.themoviedb.org/settings/api
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search_movies(
        self,
        query: str,
        year: Optional[int] = None
    ) -> List[Movie]:
        """Search for movies by title."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/search/movie",
                params={
                    "api_key": self.api_key,
                    "query": query,
                    "year": year,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            movies = []
            for item in data.get("results", [])[:10]:
                movies.append(Movie(
                    id=item["id"],
                    title=item["title"],
                    overview=item.get("overview", ""),
                    release_date=date.fromisoformat(item["release_date"]) 
                        if item.get("release_date") else None,
                    rating=item.get("vote_average", 0),
                    poster_url=f"{self.IMAGE_BASE_URL}{item['poster_path']}"
                        if item.get("poster_path") else None,
                    genres=[],  # Need separate call for genre names
                    runtime_minutes=None
                ))
            
            return movies
    
    async def get_now_playing(
        self,
        region: str = "EG"
    ) -> List[Movie]:
        """Get movies currently in theaters."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/movie/now_playing",
                params={
                    "api_key": self.api_key,
                    "region": region,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                Movie(
                    id=item["id"],
                    title=item["title"],
                    overview=item.get("overview", ""),
                    release_date=date.fromisoformat(item["release_date"])
                        if item.get("release_date") else None,
                    rating=item.get("vote_average", 0),
                    poster_url=f"{self.IMAGE_BASE_URL}{item['poster_path']}"
                        if item.get("poster_path") else None,
                    genres=[],
                    runtime_minutes=None
                )
                for item in data.get("results", [])
            ]
    
    async def get_movie_details(self, movie_id: int) -> Movie:
        """Get detailed information about a movie."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/movie/{movie_id}",
                params={"api_key": self.api_key}
            )
            response.raise_for_status()
            item = response.json()
            
            return Movie(
                id=item["id"],
                title=item["title"],
                overview=item.get("overview", ""),
                release_date=date.fromisoformat(item["release_date"])
                    if item.get("release_date") else None,
                rating=item.get("vote_average", 0),
                poster_url=f"{self.IMAGE_BASE_URL}{item['poster_path']}"
                    if item.get("poster_path") else None,
                genres=[g["name"] for g in item.get("genres", [])],
                runtime_minutes=item.get("runtime")
            )
```

---

## Tier 2: Web Automation

### Playwright Setup

```python
# backend/app/automation/browser.py

from playwright.async_api import async_playwright, Browser, Page
from typing import Optional
import asyncio

class BrowserManager:
    """
    Manages browser instances for web automation.
    """
    
    _instance: Optional['BrowserManager'] = None
    _browser: Optional[Browser] = None
    
    @classmethod
    async def get_instance(cls) -> 'BrowserManager':
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._initialize()
        return cls._instance
    
    async def _initialize(self):
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
    
    async def new_page(self) -> Page:
        """Create a new browser page with stealth settings."""
        context = await self._browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Add stealth scripts
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        return page
    
    async def close(self):
        if self._browser:
            await self._browser.close()
```

### Vezeeta Automation

```python
# backend/app/automation/vezeeta.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, date
from .browser import BrowserManager

@dataclass
class Doctor:
    id: str
    name: str
    specialty: str
    clinic_name: str
    address: str
    rating: float
    reviews_count: int
    consultation_fee: float
    available_slots: List[datetime]
    profile_url: str

@dataclass
class AppointmentConfirmation:
    confirmation_id: str
    doctor_name: str
    appointment_time: datetime
    clinic_address: str
    instructions: str

class VezeetaAutomation:
    """
    Web automation for Vezeeta healthcare platform.
    
    Note: This is for demonstration purposes. In production,
    you should check Vezeeta's Terms of Service and consider
    official API partnerships.
    """
    
    BASE_URL = "https://www.vezeeta.com"
    
    async def search_doctors(
        self,
        specialty: str,
        location: str,
        insurance: Optional[str] = None
    ) -> List[Doctor]:
        """
        Search for doctors on Vezeeta.
        
        Args:
            specialty: Medical specialty (e.g., "dermatologist")
            location: City or area (e.g., "Cairo")
            insurance: Insurance provider name (optional)
            
        Returns:
            List of Doctor objects with availability
        """
        browser = await BrowserManager.get_instance()
        page = await browser.new_page()
        
        try:
            # Navigate to search
            await page.goto(f"{self.BASE_URL}/en/Egypt")
            
            # Enter specialty
            await page.fill('[data-testid="search-input"]', specialty)
            await page.click('[data-testid="search-submit"]')
            
            # Wait for results
            await page.wait_for_selector('.doctor-card', timeout=10000)
            
            # Apply location filter if needed
            if location:
                await page.click('[data-testid="location-filter"]')
                await page.fill('[data-testid="location-search"]', location)
                await page.click(f'text={location}')
            
            # Apply insurance filter if specified
            if insurance:
                await page.click('[data-testid="insurance-filter"]')
                await page.click(f'text={insurance}')
            
            # Extract doctor data
            doctors = []
            doctor_cards = await page.query_selector_all('.doctor-card')
            
            for card in doctor_cards[:10]:  # Limit to 10 results
                name = await card.query_selector('.doctor-name')
                name_text = await name.inner_text() if name else "Unknown"
                
                rating = await card.query_selector('.rating-value')
                rating_text = await rating.inner_text() if rating else "0"
                
                price = await card.query_selector('.consultation-fee')
                price_text = await price.inner_text() if price else "0"
                
                # Get available slots
                slots_container = await card.query_selector('.available-slots')
                slot_elements = await slots_container.query_selector_all('.slot') if slots_container else []
                
                slots = []
                for slot in slot_elements[:5]:
                    slot_time = await slot.get_attribute('data-time')
                    if slot_time:
                        slots.append(datetime.fromisoformat(slot_time))
                
                profile_link = await card.query_selector('a.doctor-profile')
                profile_url = await profile_link.get_attribute('href') if profile_link else ""
                
                doctors.append(Doctor(
                    id=await card.get_attribute('data-doctor-id') or "",
                    name=name_text,
                    specialty=specialty,
                    clinic_name="",  # Would need to extract
                    address=location,
                    rating=float(rating_text.replace(',', '.')),
                    reviews_count=0,
                    consultation_fee=float(price_text.replace('EGP', '').strip()),
                    available_slots=slots,
                    profile_url=f"{self.BASE_URL}{profile_url}"
                ))
            
            return doctors
            
        finally:
            await page.close()
    
    async def book_appointment(
        self,
        doctor_id: str,
        slot_time: datetime,
        patient_name: str,
        patient_phone: str,
        reason: Optional[str] = None
    ) -> AppointmentConfirmation:
        """
        Book an appointment with a doctor.
        
        This function navigates through the booking flow:
        1. Select the time slot
        2. Enter patient information
        3. Confirm booking
        
        Args:
            doctor_id: Doctor's Vezeeta ID
            slot_time: Desired appointment time
            patient_name: Patient's full name
            patient_phone: Patient's phone number
            reason: Reason for visit (optional)
            
        Returns:
            AppointmentConfirmation with booking details
        """
        browser = await BrowserManager.get_instance()
        page = await browser.new_page()
        
        try:
            # Navigate to doctor's profile
            await page.goto(f"{self.BASE_URL}/en/doctor/{doctor_id}")
            
            # Find and click the desired time slot
            slot_selector = f'[data-time="{slot_time.isoformat()}"]'
            await page.click(slot_selector)
            
            # Wait for booking form
            await page.wait_for_selector('[data-testid="booking-form"]')
            
            # Fill patient information
            await page.fill('[name="patientName"]', patient_name)
            await page.fill('[name="patientPhone"]', patient_phone)
            
            if reason:
                await page.fill('[name="visitReason"]', reason)
            
            # Submit booking
            await page.click('[data-testid="confirm-booking"]')
            
            # Wait for confirmation
            await page.wait_for_selector('[data-testid="booking-confirmation"]')
            
            # Extract confirmation details
            confirmation_id = await page.locator(
                '[data-testid="confirmation-id"]'
            ).inner_text()
            
            doctor_name = await page.locator(
                '[data-testid="doctor-name"]'
            ).inner_text()
            
            clinic_address = await page.locator(
                '[data-testid="clinic-address"]'
            ).inner_text()
            
            instructions = await page.locator(
                '[data-testid="instructions"]'
            ).inner_text()
            
            return AppointmentConfirmation(
                confirmation_id=confirmation_id,
                doctor_name=doctor_name,
                appointment_time=slot_time,
                clinic_address=clinic_address,
                instructions=instructions
            )
            
        finally:
            await page.close()
```

---

## Tier 3: Device Control (Android)

### Android Accessibility Service

```kotlin
// mobile/android/app/src/main/java/com/aria/accessibility/ARIAAccessibilityService.kt

package com.aria.accessibility

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import kotlinx.coroutines.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
sealed class AgentAction {
    @Serializable
    data class Click(val target: String, val index: Int = 0) : AgentAction()
    
    @Serializable
    data class Type(val target: String, val text: String) : AgentAction()
    
    @Serializable
    data class Scroll(val direction: String) : AgentAction()
    
    @Serializable
    data class Wait(val milliseconds: Long) : AgentAction()
    
    @Serializable
    object Back : AgentAction()
    
    @Serializable
    object Home : AgentAction()
}

@Serializable
data class ActionResult(
    val success: Boolean,
    val message: String,
    val screenshot: String? = null
)

class ARIAAccessibilityService : AccessibilityService() {
    
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var actionQueue = mutableListOf<AgentAction>()
    
    override fun onServiceConnected() {
        val info = AccessibilityServiceInfo().apply {
            eventTypes = AccessibilityEvent.TYPES_ALL_MASK
            feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC
            flags = AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS or
                    AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
            notificationTimeout = 100
        }
        serviceInfo = info
    }
    
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        event?.let {
            when (it.eventType) {
                AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED -> {
                    // Log current app for debugging
                    logCurrentWindow(it)
                }
                AccessibilityEvent.TYPE_VIEW_CLICKED -> {
                    // Track user interactions
                }
            }
        }
    }
    
    override fun onInterrupt() {
        scope.cancel()
    }
    
    /**
     * Execute an action on the device.
     */
    suspend fun executeAction(action: AgentAction): ActionResult {
        return withContext(Dispatchers.Main) {
            try {
                when (action) {
                    is AgentAction.Click -> performClick(action.target, action.index)
                    is AgentAction.Type -> performType(action.target, action.text)
                    is AgentAction.Scroll -> performScroll(action.direction)
                    is AgentAction.Wait -> {
                        delay(action.milliseconds)
                        ActionResult(true, "Waited ${action.milliseconds}ms")
                    }
                    is AgentAction.Back -> {
                        performGlobalAction(GLOBAL_ACTION_BACK)
                        ActionResult(true, "Pressed back")
                    }
                    is AgentAction.Home -> {
                        performGlobalAction(GLOBAL_ACTION_HOME)
                        ActionResult(true, "Pressed home")
                    }
                }
            } catch (e: Exception) {
                ActionResult(false, "Error: ${e.message}")
            }
        }
    }
    
    /**
     * Find and click an element by text or content description.
     */
    private fun performClick(target: String, index: Int): ActionResult {
        val rootNode = rootInActiveWindow ?: return ActionResult(false, "No active window")
        
        val nodes = findNodesByText(rootNode, target)
        
        return if (nodes.isNotEmpty() && index < nodes.size) {
            val node = nodes[index]
            val clicked = node.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            
            if (clicked) {
                ActionResult(true, "Clicked on '$target'")
            } else {
                // Try clicking parent if node isn't clickable
                val parent = node.parent
                if (parent?.isClickable == true) {
                    parent.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                    ActionResult(true, "Clicked on parent of '$target'")
                } else {
                    ActionResult(false, "Element '$target' is not clickable")
                }
            }
        } else {
            ActionResult(false, "Element '$target' not found")
        }
    }
    
    /**
     * Type text into a focused element.
     */
    private fun performType(target: String, text: String): ActionResult {
        val rootNode = rootInActiveWindow ?: return ActionResult(false, "No active window")
        
        // Find the target input field
        val nodes = findNodesByText(rootNode, target)
        val inputNode = nodes.find { it.isEditable } 
            ?: findEditableNode(rootNode)
            ?: return ActionResult(false, "No editable field found")
        
        // Focus the field
        inputNode.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
        
        // Set the text
        val arguments = android.os.Bundle().apply {
            putCharSequence(
                AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                text
            )
        }
        
        val success = inputNode.performAction(
            AccessibilityNodeInfo.ACTION_SET_TEXT,
            arguments
        )
        
        return if (success) {
            ActionResult(true, "Typed '$text' into field")
        } else {
            ActionResult(false, "Failed to type text")
        }
    }
    
    /**
     * Scroll in a direction.
     */
    private fun performScroll(direction: String): ActionResult {
        val action = when (direction.lowercase()) {
            "up" -> GLOBAL_ACTION_SCROLL_BACKWARD
            "down" -> GLOBAL_ACTION_SCROLL_FORWARD
            else -> return ActionResult(false, "Invalid scroll direction")
        }
        
        val success = performGlobalAction(action)
        return ActionResult(success, if (success) "Scrolled $direction" else "Scroll failed")
    }
    
    /**
     * Find nodes matching text content.
     */
    private fun findNodesByText(
        node: AccessibilityNodeInfo,
        text: String
    ): List<AccessibilityNodeInfo> {
        val results = mutableListOf<AccessibilityNodeInfo>()
        
        // Check current node
        val nodeText = node.text?.toString() ?: ""
        val contentDesc = node.contentDescription?.toString() ?: ""
        
        if (nodeText.contains(text, ignoreCase = true) ||
            contentDesc.contains(text, ignoreCase = true)) {
            results.add(node)
        }
        
        // Check children
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { child ->
                results.addAll(findNodesByText(child, text))
            }
        }
        
        return results
    }
    
    /**
     * Find the first editable node.
     */
    private fun findEditableNode(node: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        if (node.isEditable) return node
        
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { child ->
                findEditableNode(child)?.let { return it }
            }
        }
        
        return null
    }
    
    /**
     * Get current screen content for the AI agent.
     */
    fun getScreenContent(): Map<String, Any> {
        val rootNode = rootInActiveWindow ?: return emptyMap()
        
        return mapOf(
            "packageName" to (rootNode.packageName?.toString() ?: ""),
            "elements" to extractElements(rootNode)
        )
    }
    
    private fun extractElements(node: AccessibilityNodeInfo): List<Map<String, Any>> {
        val elements = mutableListOf<Map<String, Any>>()
        
        if (node.isVisibleToUser) {
            val bounds = android.graphics.Rect()
            node.getBoundsInScreen(bounds)
            
            elements.add(mapOf(
                "text" to (node.text?.toString() ?: ""),
                "contentDescription" to (node.contentDescription?.toString() ?: ""),
                "className" to (node.className?.toString() ?: ""),
                "isClickable" to node.isClickable,
                "isEditable" to node.isEditable,
                "bounds" to mapOf(
                    "left" to bounds.left,
                    "top" to bounds.top,
                    "right" to bounds.right,
                    "bottom" to bounds.bottom
                )
            ))
        }
        
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { child ->
                elements.addAll(extractElements(child))
            }
        }
        
        return elements
    }
    
    private fun logCurrentWindow(event: AccessibilityEvent) {
        // Log for debugging purposes
        android.util.Log.d("ARIA", "Window: ${event.packageName}")
    }
}
```

### Service Configuration

```xml
<!-- mobile/android/app/src/main/res/xml/accessibility_service_config.xml -->

<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeAllMask"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagReportViewIds|flagRetrieveInteractiveWindows|flagIncludeNotImportantViews"
    android:canRetrieveWindowContent="true"
    android:canPerformGestures="true"
    android:settingsActivity="com.aria.settings.AccessibilitySettingsActivity"
    android:description="@string/accessibility_service_description"
    android:notificationTimeout="100" />
```

---

## Authentication Flow

For services requiring user authentication (Uber, Google), implement OAuth 2.0:

```python
# backend/app/auth/oauth.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import httpx
from urllib.parse import urlencode

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

@router.get("/auth/google")
async def google_auth():
    """Redirect user to Google OAuth consent screen."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.BASE_URL}/auth/google/callback",
        "response_type": "code",
        "scope": " ".join([
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/userinfo.email"
        ]),
        "access_type": "offline",
        "prompt": "consent"
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")

@router.get("/auth/google/callback")
async def google_callback(code: str):
    """Handle OAuth callback and exchange code for tokens."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.BASE_URL}/auth/google/callback"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(400, "Failed to exchange code")
        
        tokens = response.json()
        
        # Store tokens securely
        await store_user_tokens(
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            expires_in=tokens["expires_in"]
        )
        
        return {"message": "Google Calendar connected successfully"}
```

---

## Error Handling

```python
# backend/app/tools/base.py

class IntegrationError(Exception):
    """Base exception for integration errors."""
    pass

class RateLimitError(IntegrationError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")

class AuthenticationError(IntegrationError):
    """Raised when authentication fails."""
    pass

class ServiceUnavailableError(IntegrationError):
    """Raised when external service is unavailable."""
    pass

async def with_retry(func, max_retries=3, backoff=2.0):
    """Execute function with exponential backoff retry."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError as e:
            await asyncio.sleep(e.retry_after)
        except ServiceUnavailableError:
            await asyncio.sleep(backoff ** attempt)
            last_error = e
        except AuthenticationError:
            raise  # Don't retry auth errors
    
    raise last_error or IntegrationError("Max retries exceeded")
```
]]>
