
from typing import Callable

from arkalos.http import Middleware, Request, Response

class MAKEMiddleware(Middleware):

    async def __call__(self, req: Request, next: Callable) -> Response:

        resp = await next(req)

        return resp
