
from typing import Type, Callable, Awaitable, Any, Protocol
from enum import IntEnum

import random
import asyncio
import re
import json

from playwright.async_api import (
    Playwright, 
    async_playwright, 
    expect, 
    Browser, 
    BrowserContext, 
    Page,
    Route
)



class WebBrowserType(IntEnum):
    REMOTE_CDP = 1
    EDGE_HEADLESS = 2
    EDGE_UI = 3
    CHROME_HEADLESS = 4
    CHROME_UI = 5
    FIREFOX_HEADLESS = 6
    FIREFOX_UI = 7
    SAFARI_HEADLESS = 8
    SAFARI_UI = 9

class WebBrowserCallback(Protocol):
    def __call__(self, tab: Page, *args: Any, **kwargs: Any) -> Awaitable[Any]:
        ...

class WebBrowser:

    TYPE: Type[WebBrowserType] = WebBrowserType
    REMOTE_HOST_PORT: str = 'http://localhost:9222'

    _TEST_HEADERS_URL = 'https://httpbin.org/headers'
    _TEST_COOKIES_URL = 'https://httpbin.org/cookies'
    _TEST_IP_URL = 'https://httpbin.org/ip'

    _type: WebBrowserType
    _blockResources: bool
    _browser: Browser
    _context: BrowserContext



    def __init__(self, type: WebBrowserType = WebBrowserType.EDGE_HEADLESS, block_resources = False) -> None:
        '''
        Initialize WebBrowser with specific browser type.
        
        Args:
            type: Browser type to launch, defaults to Edge headless
        '''
        self._type = type
        self._blockResources = block_resources

    

    @staticmethod
    async def scroll(tab: Page, scroll_amount=300, delay_min=0.01, delay_max=0.01):
        #viewport_height = tab.viewport_size['height'] # type: ignore
        viewport_height = await tab.evaluate('window.innerHeight')
        current_scroll_position = await tab.evaluate('window.scrollY')
        document_height = await tab.evaluate('document.body.scrollHeight')

        while current_scroll_position + viewport_height < document_height:
            # Scroll by random amount +-scroll_amount during a single tick
            scroll_step = random.randint(int(scroll_amount * 0.7), int(scroll_amount * 1.3))
            await tab.evaluate(f'window.scrollBy(0, {scroll_step})')

            # Wait for random time
            scroll_delay = random.uniform(delay_min, delay_max)
            await asyncio.sleep(scroll_delay)

            current_scroll_position = await tab.evaluate("window.scrollY")

    @staticmethod
    async def clickByText(tab: Page, text: str):
        await tab.get_by_text(text).hover()
        await tab.get_by_text(text).click()



    async def run(self, fn: WebBrowserCallback, *args, **kwargs) -> Any:
        '''
        Run a browser automation function.
        
        Args:
            fn: Callback function that receives a Page object
        '''
        async with async_playwright() as playwright:
            await self._createBrowserContext(self._type, playwright)
            page = await self._context.new_page() # new tab
            if self._blockResources:
                await page.route('**/*', self._handleBlockResources)
            res = await fn(page, *args, **kwargs)
            await self._context.close()
            await self._browser.close()

        return res
        
    def runWithinSync(self, fn: WebBrowserCallback, *args, **kwargs) -> Any:
        return asyncio.run(self.run(fn, *args, **kwargs))

    async def testHeadersCookiesIP(self):
        urls = [
            self._TEST_HEADERS_URL,
            self._TEST_COOKIES_URL,
            self._TEST_IP_URL
        ]
        res = await self.run(self._requestContent, urls)
        return res



    async def _request(self, tab: Page, url: str):
        response = await tab.goto(url)
        if response:
            if 'content-type' in response.headers and response.headers['content-type'] == 'application/json':
                return await response.json()
            return await tab.content()
        return None

    async def _requestContent(self, tab: Page, url: str|list[str]):
            if isinstance(url, list):
                res: dict = {}
                for link in url:
                    data = await self._request(tab, link)
                    res = res | data
                return res
            return await self._request(tab, url)

    async def _createBrowserContext(self, type: WebBrowserType, playwright: Playwright) -> None:
        if type == WebBrowserType.REMOTE_CDP:
            await self._createRemoteCDPBrowser(playwright)
        elif type == WebBrowserType.EDGE_HEADLESS:
            await self._createEdgeBrowser(True, playwright)
        elif type == WebBrowserType.EDGE_UI:
            await self._createEdgeBrowser(False, playwright)
        elif type == WebBrowserType.CHROME_HEADLESS:
            await self._createChromeBrowser(True, playwright)
        elif type == WebBrowserType.CHROME_UI:
            await self._createChromeBrowser(False, playwright)
        elif type == WebBrowserType.FIREFOX_HEADLESS:
            await self._createFirefoxBrowser(True, playwright)
        elif type == WebBrowserType.FIREFOX_UI:
            await self._createFirefoxBrowser(False, playwright)
        elif type == WebBrowserType.SAFARI_HEADLESS:
            await self._createSafariBrowser(True, playwright)
        elif type == WebBrowserType.SAFARI_UI:
            await self._createSafariBrowser(False, playwright)

    async def _createRemoteCDPBrowser(self, playwright: Playwright) -> None:
        self._browser = await playwright.chromium.connect_over_cdp(WebBrowser.REMOTE_HOST_PORT, timeout=10000)
        self._context = self._browser.contexts[0]

    async def _createChromiumBrowser(self, channel: str, headless: bool, playwright: Playwright) -> None:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        self._browser = await playwright.chromium.launch(channel=channel, headless=headless)
        device_config = playwright.devices['Desktop Edge']
        self._context = await self._browser.new_context(**device_config)

    async def _createEdgeBrowser(self, headless: bool, playwright: Playwright) -> None:
        await self._createChromiumBrowser('msedge', headless, playwright)

    async def _createChromeBrowser(self, headless: bool, playwright: Playwright) -> None:
        await self._createChromiumBrowser('chrome', headless, playwright)

    async def _createFirefoxBrowser(self, headless: bool, playwright: Playwright) -> None:
        self._browser = await playwright.firefox.launch(headless=headless)
        device_config = playwright.devices['Desktop Firefox']
        self._context = await self._browser.new_context(**device_config)

    async def _createSafariBrowser(self, headless: bool, playwright: Playwright) -> None:
        self._browser = await playwright.webkit.launch(headless=headless)
        device_config = playwright.devices['Desktop Safari']
        self._context = await self._browser.new_context(**device_config)

    async def _handleBlockResources(self, route: Route) -> None:
        if route.request.resource_type in ['image', 'stylesheet', 'media', 'font']:
            return await route.abort()
        return await route.continue_()
