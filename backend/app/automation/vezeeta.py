<![CDATA["""
Vezeeta Automation
Web automation for booking medical appointments on Vezeeta.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import structlog

from app.automation.browser import BrowserManager

logger = structlog.get_logger()


@dataclass
class VezeetaDoctor:
    """Doctor information from Vezeeta."""
    id: str
    name: str
    specialty: str
    clinic: str
    address: str
    rating: float
    reviews_count: int
    consultation_fee: float
    currency: str
    available_slots: List[str]
    profile_url: str


@dataclass
class VezeetaAppointment:
    """Appointment confirmation details."""
    confirmation_id: str
    doctor_name: str
    specialty: str
    appointment_time: str
    clinic: str
    address: str
    instructions: List[str]


class VezeetaAutomation:
    """
    Web automation for Vezeeta healthcare platform.
    
    This class handles:
    - Searching for doctors by specialty
    - Getting available appointment slots
    - Booking appointments
    - Managing existing appointments
    
    Note: This is for demonstration purposes. In production,
    consider:
    1. Vezeeta's Terms of Service
    2. Rate limiting to avoid overloading their servers
    3. Error handling for site changes
    4. User consent for automated actions
    """
    
    BASE_URL = "https://www.vezeeta.com"
    
    def __init__(self):
        self.browser_manager: Optional[BrowserManager] = None
    
    async def _get_browser(self) -> BrowserManager:
        """Get browser manager instance."""
        if not self.browser_manager:
            self.browser_manager = await BrowserManager.get_instance()
        return self.browser_manager
    
    async def search_doctors(
        self,
        specialty: str,
        location: str,
        insurance: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Search for doctors on Vezeeta.
        
        Args:
            specialty: Medical specialty (e.g., "dermatologist")
            location: City or area (e.g., "Cairo", "Nasr City")
            insurance: Optional insurance provider filter
            language: Website language (en/ar)
            
        Returns:
            Dictionary with list of doctors and metadata
        """
        browser = await self._get_browser()
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            logger.info(
                "Searching doctors on Vezeeta",
                specialty=specialty,
                location=location
            )
            
            # Navigate to Vezeeta
            await page.goto(f"{self.BASE_URL}/{language}/Egypt", timeout=30000)
            await browser.wait_for_network_idle(page)
            
            # Search for specialty
            # Note: Selectors are examples - actual selectors may differ
            search_input = '[data-testid="search-input"], input[placeholder*="Search"]'
            
            if await browser.safe_fill(page, search_input, specialty):
                await page.keyboard.press('Enter')
                await browser.wait_for_network_idle(page)
            
            # Wait for results to load
            await page.wait_for_selector('.doctor-card, [data-testid="doctor-card"]', timeout=15000)
            
            # Apply location filter if available
            location_filter = '[data-testid="location-filter"], .location-filter'
            if await page.locator(location_filter).count() > 0:
                await page.click(location_filter)
                await page.fill('[data-testid="location-search"]', location)
                # Select from dropdown
                await page.click(f'text="{location}"')
                await browser.wait_for_network_idle(page)
            
            # Apply insurance filter if specified
            if insurance:
                insurance_filter = '[data-testid="insurance-filter"]'
                if await page.locator(insurance_filter).count() > 0:
                    await page.click(insurance_filter)
                    await page.click(f'text="{insurance}"')
                    await browser.wait_for_network_idle(page)
            
            # Extract doctor data
            doctors = await self._extract_doctors(page)
            
            return {
                "success": True,
                "specialty": specialty,
                "location": location,
                "insurance_filter": insurance,
                "doctors": doctors,
                "total_found": len(doctors),
                "source": "vezeeta",
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Doctor search failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "specialty": specialty,
                "location": location,
                "doctors": [],
                "total_found": 0
            }
            
        finally:
            await context.close()
    
    async def _extract_doctors(self, page) -> List[Dict[str, Any]]:
        """Extract doctor information from search results."""
        doctors = []
        
        # Get all doctor cards
        cards = await page.locator('.doctor-card, [data-testid="doctor-card"]').all()
        
        for i, card in enumerate(cards[:10]):  # Limit to 10 results
            try:
                doctor = {
                    "id": f"doc_{i}",
                    "name": "",
                    "specialty": "",
                    "clinic": "",
                    "address": "",
                    "rating": 0.0,
                    "reviews_count": 0,
                    "consultation_fee": 0,
                    "currency": "EGP",
                    "available_slots": [],
                    "profile_url": ""
                }
                
                # Extract name
                name_elem = card.locator('.doctor-name, [data-testid="doctor-name"]')
                if await name_elem.count() > 0:
                    doctor["name"] = await name_elem.first.inner_text()
                
                # Extract rating
                rating_elem = card.locator('.rating, [data-testid="rating"]')
                if await rating_elem.count() > 0:
                    rating_text = await rating_elem.first.inner_text()
                    try:
                        doctor["rating"] = float(rating_text.replace(',', '.'))
                    except ValueError:
                        pass
                
                # Extract price
                price_elem = card.locator('.price, [data-testid="consultation-fee"]')
                if await price_elem.count() > 0:
                    price_text = await price_elem.first.inner_text()
                    # Extract numeric value
                    import re
                    numbers = re.findall(r'\d+', price_text)
                    if numbers:
                        doctor["consultation_fee"] = int(numbers[0])
                
                # Extract profile URL
                link_elem = card.locator('a[href*="/doctor/"]')
                if await link_elem.count() > 0:
                    href = await link_elem.first.get_attribute('href')
                    doctor["profile_url"] = f"{self.BASE_URL}{href}" if href else ""
                    # Extract doctor ID from URL
                    if href:
                        doctor["id"] = href.split('/')[-1]
                
                doctors.append(doctor)
                
            except Exception as e:
                logger.warning(f"Failed to extract doctor {i}: {e}")
                continue
        
        return doctors
    
    async def get_available_slots(
        self,
        doctor_id: str,
        date: str
    ) -> Dict[str, Any]:
        """
        Get available appointment slots for a doctor.
        
        Args:
            doctor_id: Doctor's Vezeeta ID or profile path
            date: Date to check (YYYY-MM-DD)
            
        Returns:
            Dictionary with available time slots
        """
        browser = await self._get_browser()
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to doctor's profile
            profile_url = f"{self.BASE_URL}/en/doctor/{doctor_id}"
            await page.goto(profile_url, timeout=30000)
            await browser.wait_for_network_idle(page)
            
            # Select date if date picker is available
            # Implementation depends on Vezeeta's actual UI
            
            # Extract available slots
            slots = []
            slot_elements = await page.locator('[data-testid="time-slot"], .available-slot').all()
            
            for slot in slot_elements:
                slot_time = await slot.get_attribute('data-time')
                if slot_time:
                    slots.append(slot_time)
            
            return {
                "success": True,
                "doctor_id": doctor_id,
                "date": date,
                "available_slots": slots,
                "total_slots": len(slots)
            }
            
        except Exception as e:
            logger.error("Failed to get slots", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "doctor_id": doctor_id,
                "date": date,
                "available_slots": []
            }
            
        finally:
            await context.close()
    
    async def book_appointment(
        self,
        doctor_id: str,
        slot_time: str,
        patient_name: str,
        patient_phone: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Book an appointment with a doctor.
        
        Args:
            doctor_id: Doctor's Vezeeta ID
            slot_time: Appointment time (ISO 8601)
            patient_name: Patient's full name
            patient_phone: Contact phone number
            reason: Optional reason for visit
            
        Returns:
            Appointment confirmation details
        """
        browser = await self._get_browser()
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            logger.info(
                "Booking appointment",
                doctor_id=doctor_id,
                slot_time=slot_time
            )
            
            # Navigate to doctor's profile
            profile_url = f"{self.BASE_URL}/en/doctor/{doctor_id}"
            await page.goto(profile_url, timeout=30000)
            await browser.wait_for_network_idle(page)
            
            # Select the time slot
            slot_selector = f'[data-time="{slot_time}"], [data-testid="slot-{slot_time}"]'
            if not await browser.safe_click(page, slot_selector):
                raise Exception(f"Could not find slot for {slot_time}")
            
            # Wait for booking form
            await page.wait_for_selector('[data-testid="booking-form"], .booking-form', timeout=10000)
            
            # Fill patient information
            await browser.safe_fill(page, '[name="patientName"], [data-testid="patient-name"]', patient_name)
            await browser.safe_fill(page, '[name="patientPhone"], [data-testid="patient-phone"]', patient_phone)
            
            if reason:
                await browser.safe_fill(page, '[name="visitReason"], [data-testid="visit-reason"]', reason)
            
            # Submit booking
            submit_button = '[data-testid="confirm-booking"], button[type="submit"]'
            await browser.safe_click(page, submit_button)
            
            # Wait for confirmation
            await page.wait_for_selector('[data-testid="booking-confirmation"], .confirmation', timeout=30000)
            
            # Extract confirmation details
            confirmation_id = await page.locator('[data-testid="confirmation-id"]').inner_text()
            
            return {
                "success": True,
                "confirmation_id": confirmation_id.strip() if confirmation_id else f"CONF_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "doctor_id": doctor_id,
                "appointment_time": slot_time,
                "patient_name": patient_name,
                "status": "confirmed"
            }
            
        except Exception as e:
            logger.error("Booking failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "doctor_id": doctor_id,
                "appointment_time": slot_time
            }
            
        finally:
            await context.close()
]]>
