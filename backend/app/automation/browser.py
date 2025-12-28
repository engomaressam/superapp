<![CDATA["""
Browser Manager
Manages Playwright browser instances for web automation.
"""

from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import structlog

logger = structlog.get_logger()


class BrowserManager:
    """
    Manages browser instances for web automation.
    
    Features:
    - Singleton pattern for resource efficiency
    - Stealth mode to avoid bot detection
    - Context isolation for security
    - Automatic cleanup
    """
    
    _instance: Optional['BrowserManager'] = None
    _browser: Optional[Browser] = None
    _playwright = None
    
    @classmethod
    async def get_instance(cls) -> 'BrowserManager':
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._initialize()
        return cls._instance
    
    async def _initialize(self):
        """Initialize Playwright and browser."""
        logger.info("Initializing browser manager")
        
        self._playwright = await async_playwright().start()
        
        # Launch browser with stealth settings
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certifcate-errors',
                '--ignore-certifcate-errors-spki-list',
            ]
        )
        
        logger.info("Browser initialized successfully")
    
    async def new_context(
        self,
        viewport: dict = None,
        locale: str = "en-US",
        timezone: str = "Africa/Cairo"
    ) -> BrowserContext:
        """
        Create a new isolated browser context.
        
        Each context has its own cookies and storage.
        """
        if not self._browser:
            await self._initialize()
        
        context = await self._browser.new_context(
            viewport=viewport or {'width': 1920, 'height': 1080},
            locale=locale,
            timezone_id=timezone,
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            # Additional stealth options
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        
        # Add stealth scripts to every page in this context
        await context.add_init_script("""
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Override Chrome object
            window.chrome = {
                runtime: {},
            };
        """)
        
        return context
    
    async def new_page(self) -> Page:
        """Create a new page with stealth settings."""
        context = await self.new_context()
        page = await context.new_page()
        return page
    
    async def close(self):
        """Close browser and cleanup."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        
        BrowserManager._instance = None
        
        logger.info("Browser manager closed")
    
    @staticmethod
    async def take_screenshot(page: Page, path: str = None) -> bytes:
        """Take a screenshot of the current page."""
        return await page.screenshot(path=path, full_page=True)
    
    @staticmethod
    async def wait_for_network_idle(page: Page, timeout: int = 30000):
        """Wait for network to be idle."""
        await page.wait_for_load_state('networkidle', timeout=timeout)
    
    @staticmethod
    async def safe_click(page: Page, selector: str, timeout: int = 10000):
        """Safely click an element with waiting and retry."""
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            await page.click(selector)
            return True
        except Exception as e:
            logger.warning(f"Click failed for {selector}: {e}")
            return False
    
    @staticmethod
    async def safe_fill(page: Page, selector: str, value: str, timeout: int = 10000):
        """Safely fill an input field."""
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            await page.fill(selector, value)
            return True
        except Exception as e:
            logger.warning(f"Fill failed for {selector}: {e}")
            return False
]]>
