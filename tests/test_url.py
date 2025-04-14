import pytest

from arkalos.utils.url import URLSearchParams, URL

# URLSearchParams

def test_url_search_params():
    test_cases = {
        'arg=1&arg2=2': 'arg=1&arg2=2',
        '?query=one' : 'query=one',
        'https://localhost' : 'https%3A%2F%2Flocalhost=',
        'arg=Hello World': 'arg=Hello+World',
    }

    for input in test_cases:
        output = test_cases[input]
        urlp = URLSearchParams(input)
        assert urlp.toString() == output
        assert str(urlp) == output

def test_url_search_params_updates():
    urlp = URLSearchParams('one=1')
    assert urlp.get('one') == '1'
    assert urlp.get('two') == None
    assert urlp.has('one') == True
    assert urlp.has('two') == False

    urlp.set('two', 2)
    assert urlp.get('two') == '2'
    assert urlp.has('two') == True

    urlp = URLSearchParams('foo=1&bar=2')
    urlp.append('foo', 4)
    assert urlp.getAll('foo') == ['1','4']

# URL

def test_url():
    test_cases = [
        {
            'url': 'https://arkalos.com/path/to/resource?a=1&b=2&b=3',
            'href': 'https://arkalos.com/path/to/resource?a=1&b=2&b=3',
            'protocol': 'https:',
            'hostname': 'arkalos.com',
            'port': '',
            'pathname': '/path/to/resource',
            'search': '?a=1&b=2&b=3',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'http://domain.com',
            'href': 'http://domain.com/',
            'protocol': 'http:',
            'hostname': 'domain.com',
            'port': '',
            'pathname': '/',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'http://domain.com/',
            'href': 'http://domain.com/',
            'protocol': 'http:',
            'hostname': 'domain.com',
            'port': '',
            'pathname': '/',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'domain.com',
            '_ERROR': "URL constructor: 'domain.com' is not a valid URL",
        },
        {
            'url': '/',
            '_ERROR': "URL constructor: '/' is not a valid URL",
        },
        {
            'url': 'http://domain.com/path',
            'href': 'http://domain.com/path',
            'protocol': 'http:',
            'hostname': 'domain.com',
            'port': '',
            'pathname': '/path',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'http://domain.com?a=1',
            'href': 'http://domain.com/?a=1',
            'protocol': 'http:',
            'hostname': 'domain.com',
            'port': '',
            'pathname': '/',
            'search': '?a=1',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'https://sub.domain.com/path?a=1&b',
            'href': 'https://sub.domain.com/path?a=1&b',
            'protocol': 'https:',
            'hostname': 'sub.domain.com',
            'port': '',
            'pathname': '/path',
            'search': '?a=1&b',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'http://localhost',
            'href': 'http://localhost/',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '',
            'pathname': '/',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'http://localhost/#host',
            'href': 'http://localhost/#host',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '',
            'pathname': '/',
            'search': '',
            'hash': '#host',
            '_ERROR': '',
        },
        {
            'url': 'http://localhost:8080',
            'href': 'http://localhost:8080/',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '8080',
            'pathname': '/',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'http://localhost:8080/path?a=1',
            'href': 'http://localhost:8080/path?a=1',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '8080',
            'pathname': '/path',
            'search': '?a=1',
            'hash': '',
            '_ERROR': '',
        },
        {
            'url': 'https://example.com:8080/path/to/resource?search=python#section1',
            'href': 'https://example.com:8080/path/to/resource?search=python#section1',
            'protocol': 'https:',
            'hostname': 'example.com',
            'port': '8080',
            'pathname': '/path/to/resource',
            'search': '?search=python',
            'hash': '#section1',
            '_ERROR': '',
        },
        {
            'url': 'https://example.com:8080/path/to/resource#section1?search=python',
            'href': 'https://example.com:8080/path/to/resource#section1?search=python',
            'protocol': 'https:',
            'hostname': 'example.com',
            'port': '8080',
            'pathname': '/path/to/resource',
            'search': '',
            'hash': '#section1?search=python',
            '_ERROR': '',
        },
        {
            'url': 'ftp://ftp.example.org/resource',
            'href': 'ftp://ftp.example.org/resource',
            'protocol': 'ftp:',
            'hostname': 'ftp.example.org',
            'port': '',
            'pathname': '/resource',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        ## with Base URL
        {
            'base_url': 'localhost',
            'url': 'page',
            '_ERROR': "URL constructor: 'localhost' is not a valid Base URL",
        },
        {
            'base_url': 'http://localhost',
            'url': '',
            'href': 'http://localhost/',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '',
            'pathname': '/',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'base_url': 'http://localhost',
            'url': 'page',
            'href': 'http://localhost/page',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '',
            'pathname': '/page',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'base_url': 'http://localhost:8080/bar',
            'url': '/page/foo',
            'href': 'http://localhost:8080/page/foo',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '8080',
            'pathname': '/page/foo',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'base_url': 'http://localhost:8080/bar',
            'url': '/page/foo?q=one#test',
            'href': 'http://localhost:8080/page/foo?q=one#test',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '8080',
            'pathname': '/page/foo',
            'search': '?q=one',
            'hash': '#test',
            '_ERROR': '',
        },
        {
            'base_url': 'http://localhost:8080/bar',
            'url': '..',
            'href': 'http://localhost:8080/',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '8080',
            'pathname': '/',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
        {
            'base_url': 'http://localhost:8080/bar',
            'url': './home',
            'href': 'http://localhost:8080/home',
            'protocol': 'http:',
            'hostname': 'localhost',
            'port': '8080',
            'pathname': '/home',
            'search': '',
            'hash': '',
            '_ERROR': '',
        },
    ]

    for case in test_cases:
        if case['_ERROR']:
            with pytest.raises(TypeError) as e:
                url = URL(case['url'], case['base_url']) if case.get('base_url') else URL(case['url'])
            assert str(e.value) == case['_ERROR'], case['href']
            can = URL.canParse(case['url'], case['base_url']) if case.get('base_url') else URL.canParse(case['url'])
            assert can == False, case['href'] + ' canParse is not False'
        else:
            url = URL(case['url'], case['base_url']) if case.get('base_url') else URL(case['url'])
            assert url.protocol == case['protocol'], case['href']
            assert url.hostname == case['hostname'], case['href']
            assert url.port == case['port'], case['href']
            assert url.pathname == case['pathname'], case['href']
            assert url.search == case['search'], case['href']
            assert url.hash == case['hash'], case['href']
            assert url.href == case['href'], case['href']
            can = URL.canParse(case['url'], case['base_url']) if case.get('base_url') else URL.canParse(case['url'])
            assert can == True, case['href'] + ' canParse is not True'

def test_url_updates():
    url = URL('http://localhost/about')
    url.pathname = 'home'
    assert url.pathname == '/home'
    assert url.href == 'http://localhost/home'

    url.pathname = '/welcome'
    assert url.pathname == '/welcome'
    assert url.href == 'http://localhost/welcome'

    assert url.search == ''
    url.search = 'test=one'
    assert url.search == '?test=one'
    assert url.href == 'http://localhost/welcome?test=one'
