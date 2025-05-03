
import typing
from starlette.types import ASGIApp, ExceptionHandler, Lifespan, Receive, Scope, Send
from starlette.datastructures import State, URLPath
from starlette.middleware import Middleware, _MiddlewareFactory
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import BaseRoute, Router
from starlette.types import ASGIApp, ExceptionHandler, Lifespan, Receive, Scope, Send
from starlette.websockets import WebSocket
from fastapi import FastAPI


from arkalos.http.middleware.silent_server_error_middleware import SilentServerErrorMiddleware


class HTTPApp(FastAPI):

    def build_middleware_stack(self) -> ASGIApp:
            debug = self.debug
            error_handler = None
            exception_handlers: dict[typing.Any, typing.Callable[[Request, Exception], Response]] = {}

            for key, value in self.exception_handlers.items():
                if key in (500, Exception):
                    error_handler = value
                else:
                    exception_handlers[key] = value # type: ignore

            middleware = (
                 # use custom SilentServerErrorMiddleware
                [Middleware(SilentServerErrorMiddleware, handler=error_handler, debug=debug)]
                + self.user_middleware
                + [Middleware(ExceptionMiddleware, handlers=exception_handlers, debug=debug)]
            )

            app = self.router
            for cls, args, kwargs in reversed(middleware):
                app = cls(app, *args, **kwargs)
            return app