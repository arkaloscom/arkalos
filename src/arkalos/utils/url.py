import re

class URLSearchParams:

    _params: dict[str, list[str]]

    def __init__(self, query: str = ''):
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
            self._params[name].append(value)
        else:
            self._params[name] = [value]

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
        self._params[name] = [value]

    def toString(self) -> str:
        if not self._params:
            return ''
        parts = []
        for key, values in self._params.items():
            for value in values:
                parts.append(f"{key}={value}" if value else key)
        return '&'.join(parts)

    def __str__(self) -> str:
        return self.toString()


class URL:

    _rawUrl: str
    _protocol: str|None
    _hostname: str|None
    _port: str|None
    _pathname: str
    _searchParams: URLSearchParams

    def __init__(self, url: str, base: str|None = None):
        self._rawUrl = url.strip()
        self._protocol = None
        self._hostname = None
        self._port = None
        self._pathname = "/"
        self._searchParams = URLSearchParams()
        
        if base and not self._rawUrl.startswith(('http://', 'https://')):
            base_url = URL(base)
            self._protocol = base_url.protocol
            self._hostname = base_url.hostname
            self._port = base_url.port
            self._parseRelativeUrl(self._rawUrl)
        else:
            self._parseUrl(self._rawUrl)

    def _parseUrl(self, url: str) -> None:
        protocol_match = re.match(r'^([a-z]+://)?(.*)$', url)
        if protocol_match:
            protocol = protocol_match.group(1)
            if protocol:
                self._protocol = protocol[:-3]
            remaining = protocol_match.group(2)
        else:
            remaining = url

        parts = remaining.split('?', 1)
        host_path = parts[0]
        
        if len(parts) > 1:
            self._searchParams = URLSearchParams(parts[1])

        # Split host (hostname:port) and path
        host_path_parts = host_path.split('/', 1)
        host = host_path_parts[0]
        
        # Split hostname and port
        host_parts = host.split(':', 1)
        self._hostname = host_parts[0] or None
        if len(host_parts) > 1:
            self._port = host_parts[1]
        
        if len(host_path_parts) > 1:
            self._pathname = '/' + host_path_parts[1]

    def _parseRelativeUrl(self, url: str) -> None:
        parts = url.split('?', 1)
        path_part = parts[0]
        
        if len(parts) > 1:
            self._searchParams = URLSearchParams(parts[1])
        
        if path_part:
            if path_part.startswith('/'):
                self._pathname = path_part
            else:
                self._pathname = '/' + path_part

    @property
    def protocol(self) -> str | None:
        return self._protocol

    @protocol.setter
    def protocol(self, value: str) -> None:
        self._protocol = value

    @property
    def hostname(self) -> str | None:
        return self._hostname

    @hostname.setter
    def hostname(self, value: str) -> None:
        self._hostname = value

    @property
    def port(self) -> str | None:
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
        return '?' + self._searchParams.toString() if self._searchParams.toString() else ''

    @search.setter
    def search(self, value: str) -> None:
        self._searchParams = URLSearchParams(value)

    @property
    def searchParams(self) -> URLSearchParams:
        return self._searchParams

    @property
    def href(self) -> str:
        result = ''
        if self._protocol:
            result += f"{self._protocol}://"
        if self._hostname:
            result += self._hostname
        if self._port:
            result += f":{self._port}"
        result += self._pathname
        if self._searchParams.toString():
            result += '?' + self._searchParams.toString()
        return result

    def toString(self) -> str:
        return self.href

    def __str__(self) -> str:
        return self.href
