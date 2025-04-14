
import re
from typing import TypedDict
from enum import StrEnum

from bs4 import BeautifulSoup, Comment, Tag
from markdownify import markdownify as md #type: ignore

from arkalos.utils.url import URL
from arkalos.utils.dict_utils import filter_by_col
from arkalos.utils.str_utils import after



class LinkType(StrEnum):
    INT = '1_INT'
    EXT = '2_EXT'

class LinkDict(TypedDict):
    url: str
    text: str
    attr_id: str
    attr_class: str
    type: LinkType
    domain: str
    path: str
    query: str
    hash: str



class HTMLDocumentParser:
    
    STRIP_COMMENTS = True
    STRIP_TAGS = [
        'iframe',
        'script',
        'noscript',
        'style',
        'input',
        'option',
        'label',
        'textarea',
        'fieldset',
        'legend',
        'select',
        'button',
        'svg',
        'img',
        'figure',
        'figcaption',
        'picture',
        'source',
        'video'
        'audio',
        'track',
        'canvas',
        'template',
    ]
    STRIP_SELECTORS = [
        '[aria-roledescription="map"]'
    ]

    _parseEngine: BeautifulSoup
    _trailSlash: bool
    _contentSelector: str

    _rawHTML: str
    _cleanHTML: str
    _contentHTML: str
    _markdown: str

    _baseURL: str
    _domain: str
    _path: str

    _title: str|None
    _charset: str|None
    _meta: dict[str, str]
    _metaProps: dict[str, str]
    _links: list[LinkDict]
    _pageLinks: list[LinkDict]
    _internalPageLinks: list[LinkDict]
    _externalPageLinks: list[LinkDict]


    
    def __init__(self, html_str: str, base_url: str, trail_slash: bool = False, content_selector: str = ''):
        '''
        Parse the raw HTML content
        
        Args:
            html_str: Raw HTML string to parse
            base_url: Page URL
            trail_slash: Optional. Adds or removes "/" at the end of all hrefs. No trailing slash by default.
            content_selector: optional str for a CSS selector to get a markdown for, 
                i.e. main content and skip nav, menu and footer.
        '''
        self._baseURL = base_url
        self._trailSlash = trail_slash
        self._contentSelector = content_selector
        url = URL(self._baseURL)
        self._domain = url.hostname
        self._path = url.pathname
        self._query = url.search
        self._rawHTML = html_str.strip()
        self._parseEngine = BeautifulSoup(self._rawHTML, 'lxml')
        self._cleanHTML = self._clean()

        self._title = self._extractTitle()
        meta = self._extractMeta()
        self._charset = meta['charset']
        self._meta = meta['meta']
        self._metaProps = meta['meta_props']
        self._links = self._extractLinks(self._baseURL)
        self._pageLinks = self._filterUniquePageLinks(self._links)
        self._internalPageLinks = filter_by_col(self._pageLinks, 'type', LinkType.INT)
        self._externalPageLinks = filter_by_col(self._pageLinks, 'type', LinkType.EXT)

        self._contentHTML = self._getContentHTML()
        self._markdown = self._toMarkdown()

    @property 
    def url(self) -> str:
        return self._baseURL
    
    @property 
    def baseURL(self) -> str:
        return self._baseURL

    @property 
    def domain(self) -> str:
        return self._domain
    
    @property 
    def path(self) -> str:
        return self._path

    @property
    def charset(self) -> str|None:
        return self._charset
    
    @property
    def title(self) -> str|None:
        return self._title
    
    @property
    def meta(self) -> dict[str, str]:
        return self._meta
    
    @property
    def metaProps(self) -> dict[str, str]:
        return self._metaProps
    
    @property
    def links(self) -> list[LinkDict]:
        return self._links
    
    @property
    def pageLinks(self) -> list[LinkDict]:
        return self._pageLinks
    
    @property
    def internalPageLinks(self) -> list[LinkDict]:
        return self._internalPageLinks
    
    @property
    def externalPageLinks(self) -> list[LinkDict]:
        return self._externalPageLinks
    
    @property
    def cleanHTML(self) -> str:
        return self._cleanHTML
    
    @property
    def contentHTML(self) -> str:
        return self._contentHTML
    
    @property
    def markdown(self) -> str:
        return self._markdown
    

    
    def _clean(self) -> str:
        '''
        Clean and sanitize HTML content
        
        Returns:
            Sanitized HTML string
        '''
        if HTMLDocumentParser.STRIP_COMMENTS:
            comments: list[Tag] = self._parseEngine.find_all(text=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()

        tags_to_remove: list[Tag] = self._parseEngine.find_all(HTMLDocumentParser.STRIP_TAGS)
        for tag in tags_to_remove:
            tag.decompose()
        
        return str(self._parseEngine.prettify())
    
    def _getContentHTML(self) -> str:
        if self._contentSelector:
            content_tag = self._parseEngine.select_one(self._contentSelector)
            if isinstance(content_tag, Tag) and content_tag is not None:
                return content_tag.prettify()
            raise ValueError('HTMLDocumentParser._getContent(). Element with content_selector not found')
        return self._parseEngine.prettify()
    
    def _extractTitle(self) -> str|None:
        title_tag = self._parseEngine.find('title')
        return title_tag.string.strip() if title_tag and title_tag.string else None # type: ignore
    
    def _extractMeta(self) -> dict:
        meta_info = {
            'charset': '',
            'meta': {},
            'meta_props': {}
        }

        meta_tags = self._parseEngine.find_all('meta')
        
        for meta in meta_tags:
            if 'charset' in meta.attrs:
                meta_info['charset'] = meta['charset']
            elif 'name' in meta.attrs:
                meta_info['meta'][meta['name']] = meta.get('content', '').strip() # type: ignore
            elif 'property' in meta.attrs:
                meta_info['meta_props'][meta['property']] = meta.get('content', '').strip() # type: ignore
        
        return meta_info
    
    def querySelectorAll(self, selector) -> list[Tag]:
        return self._parseEngine.select(selector)
    
    def _querySelectorAllLinks(self) -> list[Tag]:
        # get only links with href
        return self._parseEngine.find_all('a', href=True)
    
    def _getTagAttrStr(self, tag: Tag, attr: str) -> str:
        val = tag.get(attr, '')
        if isinstance(val, list):
            val = ' '.join(val)
        return val

    def _extractLinks(self, page_url: str) -> list[LinkDict]:
        links = []
        link_tags = self._querySelectorAllLinks()
        domain = URL(page_url).hostname
        for link in link_tags:
            href = self._getTagAttrStr(link, 'href')
            href = href.strip()
            url = URL(href) if URL.canParse(href) else URL(href, page_url)
            if url:
                # Add or remove a trailing / to avoid duplicates
                if self._trailSlash:
                    url.pathname = url.pathname + '/' if url.pathname[-1] != '/' else url.pathname
                else:
                    url.pathname = url.pathname.rstrip('/')
                text = link.get_text().strip()
                link_id = self._getTagAttrStr(link, 'id')
                link_class = self._getTagAttrStr(link, 'class')

                links.append(LinkDict(
                    url=url.href,
                    text=text,
                    attr_id=link_id,
                    attr_class=link_class,
                    type=LinkType.INT if url.hostname == domain else LinkType.EXT,
                    domain=url.hostname,
                    path=url.pathname,
                    query=url.search,
                    hash=url.hash
                ))
        
        return links
    
    def _filterUniquePageLinks(self, links: list[LinkDict]) -> list[LinkDict]:
        filt_links_dict: dict[str, LinkDict] = {} # href => LinkDict for faster lookup

        for link in links:
            if not (link['path'] == '/' and link['query'] == '' and link['hash'] != ''):
                href = link['url']
                if href in filt_links_dict:
                    exist_link = filt_links_dict[href]
                    # If the existing entry has no text but the new link does, update it
                    if exist_link['text'] == '' and link['text'] != '':
                        exist_link['text'] = link['text']
                else:
                    filt_links_dict[href] = link

        return list(filt_links_dict.values())
    
    def _mdLangCallback(self, el: Tag):
        cls_attr: list[str] = el.get_attribute_list('class', [])
        for cls in cls_attr:
            if cls.startswith('language-'):
                return after(cls, 'language-')
        if el.parent:
            cls_attr = el.parent.get_attribute_list('class', [])
            for cls in cls_attr:
                if cls.startswith('language-'):
                    return after(cls, 'language-')
        return ''

    
    def _toMarkdown(self) -> str:
        '''
        Convert HTML to Markdown
        
        Returns:
            Markdown formatted string
        '''
        
        # Options:
        # https://github.com/matthewwithanm/python-markdownify?tab=readme-ov-file#options
        return md(
            self._contentHTML,
            beautiful_soup_parser='lxml',
            heading_style='ATX',        # Use # style headings
            bullets='-',  
            autolinks=True,
            code_language_callback=self._mdLangCallback,
            escape_asterisks=False,     # Don't escape asterisks for bold/italic
            escape_underscores=False,   # Don't escape underscores for bold/italic
            newline_style='spaces',     # Use spaces to join lines within paragraphs
            wrap=False,                 # Disable wrapping
        )
