from fastapi import APIRouter
from arkalos.core.registry import Registry
from arkalos.http.server import HTTPServer

Registry.register('http_server', HTTPServer)

def http_server() -> HTTPServer:
    return Registry.get('http_server')

router = http_server().getRouter()
