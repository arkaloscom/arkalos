
# Python implementation of the living URL and URLSearchParams WHATWG Web Standard.
# By Mev-Rael. Part of arkalos.utils.
# https://url.spec.whatwg.org/#url-class
# https://url.spec.whatwg.org/#interface-urlsearchparams
# https://developer.mozilla.org/en-US/docs/Web/API/URL_API
# https://developer.mozilla.org/en-US/docs/Web/API/URL
#
# Protocol will have ":" at the end.
# Path always will be at least "/", e.g. for main page
# Search (query) will have "?" at the start.
# Hash (anchor) will have "#" at the start.
# toString(), toJSON() and str(url) just return the href string.
# Object props: search, hash will be empty strings if they have no value
# Throws an exception if URL is invalid when using URL(). URL must have a protocol and hostname.
# URL.parse() and URL.canParse() can be used to avoid exceptions. parse() returns None if URL is invalid.
#
# Currently does NOT support these keys: username, password, host, origin
#
# CUSTOM FEATURES THAT ARE PYTHON-SPECIFIC AND ARE NOT PART OF THE SPEC:
# URL:
#   toDict() - export object as dict, e.g. {'protocol': ..., 'hostname': etc}. Useful for dataframes.
#   static URL.parseToDict() - Error-free creation of the dict or None if URL is invalid
# Custom URLDict(TypedDict) class

import re
from typing import Literal, TypedDict, Self
from urllib.parse import quote_plus



class URLDict(TypedDict):
    href: str
    protocol: str
    hostname: str
    port: str
    pathname: str
    search: str
    hash: str



class URLSearchParams:

    _params: dict[str, list[str]]

    def __init__(self, query: str = ''):
        query = '' if query is None else query
        self._params = {}
        if query.startswith('?'):
            query = query[1:]
        if query:
            self._parseQuery(query)

    def _parseQuery(self, query: str) -> None:
        pairs = query.split('&')
        for pair in pairs:
            if pair:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    self.append(key, value)
                else:
                    self.append(pair, '')

    def append(self, name: str, value: str) -> None:
        if name in self._params:
            self._params[name].append(str(value))
        else:
            self._params[name] = [str(value)]

    def delete(self, name: str) -> None:
        self._params.pop(name, None)

    def get(self, name: str) -> str | None:
        values = self._params.get(name)
        return values[0] if values else None

    def getAll(self, name: str) -> list[str]:
        return self._params.get(name, []).copy()

    def has(self, name: str) -> bool:
        return name in self._params

    def set(self, name: str, value: str) -> None:
        self._params[name] = [str(value)]

    def toString(self) -> str:
        if not self._params:
            return ''
        parts = []
        for key, values in self._params.items():
            for value in values:
                parts.append(f"{quote_plus(key, safe='')}={quote_plus(value, safe='')}")
        return '&'.join(parts)

    def __str__(self) -> str:
        return self.toString()



class URL:

    _rawUrl: str
    _protocol: str
    _hostname: str
    _port: str
    _pathname: str
    _searchParams: URLSearchParams
    _hash: str



    def __init__(self, url: str|Self, base: str|Self|None = None):

        if isinstance(url, URL):
            url = url.href

        if isinstance(base, URL):
            base = base.href

        if base is not None:
            parts = URL._parseUrl(base)
            if parts is False or parts['protocol'] is None or parts['domain'] is None:
                raise TypeError(f"URL constructor: '{base}' is not a valid Base URL")
            self._protocol = parts['protocol'] + ':'
            self._hostname = parts['domain']
            self._port = parts['port'] if parts['port'] is not None else ''

            url = url.lstrip('.')
            parts2 = URL._parseUrl(url)
            if not parts2:
                raise TypeError(f"URL constructor: '{url}' parse error with base")
            self._pathname = parts2['path'] if parts2['path'] else '/'
            self._pathname = '/' + self._pathname if self._pathname[0] != '/' else self._pathname
            self._hash = '#' + parts2['anchor'] if parts2['anchor'] is not None else ''
            self._searchParams = URLSearchParams(parts2['query'])
        else:
            parts = URL._parseUrl(url)
            if parts is False or parts['protocol'] is None or parts['domain'] is None:
                raise TypeError(f"URL constructor: '{url}' is not a valid URL")
            self._protocol = parts['protocol'] + ':'
            self._hostname = parts['domain']
            self._port = parts['port'] if parts['port'] is not None else ''
            self._pathname = parts['path'] if parts['path'] else '/'
            self._pathname = '/' + self._pathname if self._pathname[0] != '/' else self._pathname
            self._hash = '#' + parts['anchor'] if parts['anchor'] is not None else ''
            self._searchParams = URLSearchParams(parts['query'])
            


    @staticmethod
    def _parseUrl(url: str) -> dict|Literal[False]:
        pattern = re.compile(
            r'^(?:(?P<protocol>[a-zA-Z][a-zA-Z0-9+.-]*)://'
            r'(?P<domain>[^/:?#]+)'
            r'(?::(?P<port>\d+))?)?'
            r'(?P<path>[^?#]*)'
            r'(?:\?(?P<query>[^#]*))?'
            r'(?:#(?P<anchor>.*))?'
            r'$'
        )

        match = pattern.match(url)
        item = {
            'url': url,
            'protocol': '',
            'domain': '',
            'port': '',
            'path': '',
            'query': '',
            'anchor': ''
        }

        if match:
            for key, value in match.groupdict().items():
                item[key] = value
            return item
        else:
            return False

    @staticmethod
    def canParse(url: str, base: str|None = None) -> bool:
        '''Check if a URL string can be parsed without throwing an error.'''
        str_to_check = base if base is not None else url
        parse = URL._parseUrl(str_to_check)
        if parse is False or parse['protocol'] is None or parse['domain'] is None:
            return False
        return True

    @staticmethod
    def parse(url: str, base: str|None = None) -> 'URL|None':
        '''Exception-safe creation of the URL object. Returns None if URL is invalid'''
        if URL.canParse(url, base):
            return URL(url, base)
        return None
    
    @staticmethod
    def parseToDict(url: str, base: str|None = None) -> URLDict|None:
        '''Exception-safe creation of the dict from the URL object. Returns None if URL is invalid'''
        parsed_url = URL.parse(url, base)
        if parsed_url is None:
            return None
        return parsed_url.toDict()

    @property
    def protocol(self) -> str:
        return self._protocol

    @protocol.setter
    def protocol(self, value: str) -> None:
        self._protocol = value

    @property
    def hostname(self) -> str:
        return self._hostname

    @hostname.setter
    def hostname(self, value: str) -> None:
        self._hostname = value

    @property
    def port(self) -> str:
        return self._port

    @port.setter
    def port(self, value: str) -> None:
        self._port = value

    @property
    def pathname(self) -> str:
        return self._pathname

    @pathname.setter
    def pathname(self, value: str) -> None:
        self._pathname = value if value.startswith('/') else '/' + value

    @property
    def search(self) -> str:
        str = self._searchParams.toString()
        if str == '':
            return ''
        if str.endswith('='):
            str = str[:-1]
        return '?' + str

    @search.setter
    def search(self, value: str) -> None:
        self._searchParams = URLSearchParams(value)

    @property
    def searchParams(self) -> URLSearchParams:
        return self._searchParams

    @property
    def href(self) -> str:
        result = self.protocol + '//' + self.hostname
        if self.port:
            result += f':{self.port}'
        result += self.pathname
        if self.search:
            result += self.search
        if self.hash:
            result += self.hash
        return result
    
    @property
    def hash(self) -> str:
        return self._hash

    def toString(self) -> str:
        return self.href

    def __str__(self) -> str:
        return self.href

    def toJSON(self) -> str:
        return self.href
    
    def toDict(self) -> URLDict:
        return URLDict(
            href=self.href,
            protocol=self.protocol,
            hostname=self.hostname,
            port=self.port,
            pathname=self.pathname,
            search=self.search,
            hash=self.hash
        )
