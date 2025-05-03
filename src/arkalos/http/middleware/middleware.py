
from abc import abstractmethod

from starlette.middleware.base import BaseHTTPMiddleware

from arkalos.http.request import Request
from arkalos.http.response import Response

class Middleware:

    @abstractmethod
    async def __call__(self, request: Request, call_next) -> Response:
        pass
