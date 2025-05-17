from fastapi import APIRouter
from arkalos.core.registry import Registry
from arkalos.http.server import HTTPServer

Registry.register('http_server', HTTPServer)

def HTTP() -> HTTPServer:
    return Registry.get('http_server')

router = HTTP().getRouter()
