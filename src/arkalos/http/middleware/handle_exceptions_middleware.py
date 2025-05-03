
from typing import Callable

from arkalos.core.logger import log as Log

from arkalos.http.request import Request
from arkalos.http.response import Response, response
from arkalos.http.middleware.middleware import Middleware

from arkalos.core.config import config

class HandleExceptionsMiddleware(Middleware):

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        try:
            resp = await call_next(request)
            return resp
        except BaseException as e:
            error_type = e.__class__.__name__
            error_message = str(e) if str(e) else "(no message)"
            Log.exception(f"Unhandled exception: {e}")
            env = config('app.env', 'production')
            msg = 'Internal server error'
            if env in ['local', 'dev', 'development']:
                msg = f"{msg}: {error_type}: {error_message}"
            return response({"error": msg}, 500)
        