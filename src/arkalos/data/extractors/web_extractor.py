
import json
import re
import asyncio
from typing import overload, Type, TypedDict, Annotated as _
from types import GenericAlias
from dataclasses import dataclass, asdict

from arkalos.data.extractors.data_extractor import UnstructuredDataExtractor
from arkalos.browser import WebBrowser, WebBrowserType, WebBrowserTab
from arkalos.utils.html_utils import HTMLDocumentParser, Tag
from arkalos.utils.url import URL
from arkalos.utils.file_utils import escape_filename, create_folder
from arkalos.core.path import drive_path, get_rel_path



@dataclass
class WebDetails:
    CONTAINER: str



class WebExtractor(UnstructuredDataExtractor):

    NAME = 'WebExtractor'
    DESCRIPTION = 'Extract, scrape data from the web pages, crawl websites and extract text as Markdown or JSON using a virtual web browser'

    BROWSER_TYPE: WebBrowserType
    BASE_URL: str
    TRAIL_SLASH: bool
    PAGE_CONTENT_SELECTOR: str
    WAIT_FOR_SELECTOR: str
    CLICK_TEXT: str
    SCROLL: bool
    DETAILS: Type[WebDetails]
    JSON_DETAILS: str



    _crawledPageUrls: list
    _clickedTextFirstPage: bool

    def __init__(self, 
        base_url: str = '', 
        trail_slash: bool = False, 
        page_content_selector: str = '', 
        wait_for_selector: str = '',
        details: Type[WebDetails] = WebDetails
    ):
        self._crawledPageUrls = []
        self._clickedTextFirstPage = False
        self.BROWSER_TYPE = self.BROWSER_TYPE if hasattr(self, 'BROWSER_TYPE') else WebBrowserType.EDGE_HEADLESS
        self.BASE_URL = self.BASE_URL if hasattr(self, 'BASE_URL') else base_url
        self.TRAIL_SLASH = self.TRAIL_SLASH if hasattr(self, 'TRAIL_SLASH') else trail_slash
        self.PAGE_CONTENT_SELECTOR = self.PAGE_CONTENT_SELECTOR if hasattr(self, 'PAGE_CONTENT_SELECTOR') else page_content_selector
        self.WAIT_FOR_SELECTOR = self.WAIT_FOR_SELECTOR if hasattr(self, 'WAIT_FOR_SELECTOR') else wait_for_selector
        self.DETAILS = self.DETAILS if hasattr(self, 'DETAILS') else details
        self.CLICK_TEXT = self.CLICK_TEXT if hasattr(self, 'CLICK_TEXT') else ''
        self.SCROLL = self.SCROLL if hasattr(self, 'SCROLL') else False

    def _createBrowser(self) -> WebBrowser:
        return WebBrowser(self.BROWSER_TYPE)
    
    def _createMarkdownFile(self, url: URL, markdown_content: str):
        pathname = escape_filename(url.pathname.strip('/')) if url.pathname != '/' else '_index'
        file_path = drive_path('/crawl/' + url.hostname + '/' + pathname + '.md')
        create_folder(file_path)
        with open(file_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        print('Markdown file saved in:', get_rel_path(file_path))

    async def _requestPageContent(self, tab: WebBrowserTab, page_url, js_code: str = '') -> str|None:
        print('Opening a new page: ', page_url)
        response = await tab.goto(page_url)
        if response:
            if response.ok:
                if self.WAIT_FOR_SELECTOR:
                    await tab.wait_for_selector(self.WAIT_FOR_SELECTOR)
                elif self.PAGE_CONTENT_SELECTOR:
                    await tab.wait_for_selector(self.PAGE_CONTENT_SELECTOR)
                if self.CLICK_TEXT and not self._clickedTextFirstPage:
                    await WebBrowser.clickByText(tab, self.CLICK_TEXT)
                    self._clickedTextFirstPage = True
                if self.SCROLL:
                    await WebBrowser.scroll(tab)
                if js_code:
                    json = await tab.evaluate(js_code)
                    return json
                html = await tab.content()
                return html
            else:
                WARN = '\033[93m'
                RESET = '\033[0m'
                print(f'{WARN}Warning: Respone status is {response.status}. Skipping...{RESET}')
        return None
    
    async def _requestPageHTML(self, tab: WebBrowserTab, page_url: str) -> str|None:
        return await self._requestPageContent(tab, page_url)
    
    async def _requestPageJSON(self, tab: WebBrowserTab, page_url: str, js_code: str) -> str|None:
        return await self._requestPageContent(tab, page_url, js_code)
    
    def _getHTMLDoc(self, page_url, html: str) -> HTMLDocumentParser:
        return HTMLDocumentParser(html, page_url, self.TRAIL_SLASH, self.PAGE_CONTENT_SELECTOR)

    @overload
    async def _scrapePage(self, tab: WebBrowserTab, page_url, fn = None) -> HTMLDocumentParser|None:
        pass

    @overload
    async def _scrapePage(self, tab: WebBrowserTab, page_url, fn = None, js_code='') -> str|None:
        pass

    async def _scrapePage(self, tab: WebBrowserTab, page_url, fn = None, js_code='') -> HTMLDocumentParser|str|None:
        url = URL(page_url)
        if url.href not in self._crawledPageUrls:
            self._crawledPageUrls.append(url.href)
            if js_code:
                return await self._requestPageJSON(tab, url.href, js_code)
            html = await self._requestPageHTML(tab, url.href)
            if html:
                doc = self._getHTMLDoc(url.href, html)
                if fn:
                    return await fn(url.href, doc)
                else:
                    self._createMarkdownFile(url, doc.markdown)
                return doc
        return None
    
    async def _scrapePageHTML(self, tab: WebBrowserTab, page_url, fn = None) -> HTMLDocumentParser|None:
        return await self._scrapePage(tab, page_url, fn)
    
    async def _scrapePageJSON(self, tab: WebBrowserTab, page_url, fn = None, js_code = '') -> str|None:
        return await self._scrapePage(tab, page_url, fn, js_code)

    async def _handleCrawl(self, tab: WebBrowserTab):
        # Get the main page
        doc = await self._scrapePageHTML(tab, self.BASE_URL)
        if doc is not None:
            for link in doc.internalPageLinks:
                # Get pages linked on the main page
                page_doc = await self._scrapePageHTML(tab, link['url'])
                if page_doc is not None:
                    for page_link in page_doc.internalPageLinks:
                        # Get max nesting level 2 sub-pages
                        await self._scrapePageHTML(tab, page_link['url'])

    async def _handleSpecificPages(self, tab: WebBrowserTab, relative_urls: list[str], fn = None, js_code=''):
        final_res: list = []
        for relative_url in relative_urls:
            url = URL(relative_url, self.BASE_URL)
            if js_code:
                obj = await self._scrapePageJSON(tab, url, fn, js_code)
                if obj:
                    res = json.loads(obj)
            else:
                res = await self._scrapePageHTML(tab, url, fn)
            if isinstance(res, list):
                final_res = final_res + res
            else:
                final_res.append(res)
        return final_res
    
    def _getBrowserOpenMessage(self):
        if self.BROWSER_TYPE == WebBrowserType.REMOTE_CDP:
            return 'Connecting to your browser...'
        return 'Opening a new virtual browser...'

    async def crawl(self):
        print(self._getBrowserOpenMessage())
        browser = self._createBrowser()
        await browser.run(self._handleCrawl)
        print('Closing a browser.')

    async def crawlSpecificPages(self, relative_urls: list[str]):
        print(self._getBrowserOpenMessage())
        browser = self._createBrowser()
        await browser.run(self._handleSpecificPages, relative_urls)
        print('Closing a browser.')

    async def _extractSubtagDetail(self, url: str, doc: HTMLDocumentParser, annotation, as_type, subtag: Tag):
        val = as_type() # set default/empty value of the data type

        if subtag is None:
            return val

        # if annotated field has 3rd parameter -> parse it as attribute, slice or child index
        # otherwise just get the textContent of the tag
        if len(annotation.__metadata__) >= 2:
            annotation_item = annotation.__metadata__[1]
            if isinstance(annotation_item, int):
                # child index, get text from the child element, e.g. text node
                if len(annotation.__metadata__) == 3 and isinstance(annotation.__metadata__[2], slice):
                    # a slice, get only part of the text
                    slc = annotation.__metadata__[2]
                    val = as_type(subtag.contents[annotation_item].get_text()[slc])
                elif len(annotation.__metadata__) == 3 and '(' in annotation.__metadata__[2]:
                    # regex
                    pattern = annotation.__metadata__[2]
                    match = re.search(pattern, subtag.get_text())
                    if match:
                        val = as_type(match.group(1))
                else:
                    val = as_type(subtag.contents[annotation_item].get_text())
            elif isinstance(annotation_item, slice):
                # a slice, get only part of the text
                slc = annotation_item
                val = as_type(subtag.get_text()[slc])
            elif '(' in annotation_item:
                # regex
                pattern = annotation_item
                match = re.search(pattern, subtag.get_text())
                if match:
                    val = as_type(match.group(1))
            elif annotation_item in ['href', 'src']:
                # get full link from the href or src attribute
                val = URL(doc._getTagAttrStr(subtag, annotation_item), url).href

                if len(annotation.__metadata__) == 3 and isinstance(annotation.__metadata__[2], slice):
                    # a slice, get only part of the text
                    slc = annotation.__metadata__[2]
                    val = val[slc]
                elif len(annotation.__metadata__) == 3 and '(' in annotation.__metadata__[2]:
                    # regex
                    pattern = annotation.__metadata__[2]
                    match = re.search(pattern, val)
                    if match:
                        val = as_type(match.group(1))

            elif annotation_item is not None:
                # other attribute value
                val = as_type(doc._getTagAttrStr(subtag, annotation_item))
        else:
            val = as_type(subtag.get_text())

        return val

    async def _extractDetails(self, url: str, doc: HTMLDocumentParser) -> list[dict]:
        cls = self.DETAILS
        tags = doc.querySelectorAll(cls.CONTAINER)
        items: list[dict] = []
        for tag in tags:
            item = {}
            for prop, annotation in cls.__annotations__.items():
                as_type = annotation.__origin__
                val = as_type()
                is_list = False
                if isinstance(as_type, GenericAlias):
                    is_list = True
                    as_type = str
                selector = annotation.__metadata__[0]
                subtag: Tag|None = tag # assume that selector is not provided, then subtag = container tag itself
                if selector is not None:
                    if is_list:
                        val = []
                        subtags = tag.select(selector)
                        for subtag in subtags:
                            val.append(await self._extractSubtagDetail(url, doc, annotation, as_type, subtag))
                    else:
                        subtag = tag.select_one(selector)
                        if subtag:
                            val = await self._extractSubtagDetail(url, doc, annotation, as_type, subtag)
                elif subtag:
                    val = await self._extractSubtagDetail(url, doc, annotation, as_type, subtag)

                item[prop] = val

            items.append(item)

        return items

    async def crawlSpecificDetails(self, relative_urls: list[str], fn = None):
        if fn is None:
            fn = self._extractDetails
        
        print(self._getBrowserOpenMessage())
        browser = self._createBrowser()
        res = await browser.run(self._handleSpecificPages, relative_urls, fn)
        print('Closing a browser.')
        return res
    
    async def crawlSpecificDetailsJSON(self, relative_urls: list[str], js_code: str = ''):
        if not js_code:
            js_code = self.JSON_DETAILS
        print(self._getBrowserOpenMessage())
        browser = self._createBrowser()
        res = await browser.run(self._handleSpecificPages, relative_urls, None, js_code)
        return res

    async def getPageHTML(self, url) -> str|None:
        url = URL(url, self.BASE_URL)
        browser = self._createBrowser()
        return await browser.run(self._requestPageHTML, url.href)
    
    async def getPageHTMLDoc(self, url) -> HTMLDocumentParser|None:
        url = URL(url, self.BASE_URL)
        browser = self._createBrowser()
        html = await browser.run(self._requestPageHTML, url.href)
        if html is None:
            return None
        doc = self._getHTMLDoc(url.href, html)
        return doc
    