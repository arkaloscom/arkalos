# Due to unprofessional design and attitude,
# Starlette's ServerErrorMiddleware re-raises an exception, always
# https://github.com/encode/starlette/blob/master/starlette/middleware/errors.py#L187
# https://github.com/encode/starlette/pull/1169

# Despite adding custom handlers and middleware, it logs exceptions twice
# Silent it. Take it over in the custom HandleExceptionsMiddleware and use it in HTTPApp



from starlette.middleware.errors import ServerErrorMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

class SilentServerErrorMiddleware(ServerErrorMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await super().__call__(scope, receive, send)
        except Exception as e:
            # Swallow the exception so it doesn't propagate and get logged twice
            #raise e
            pass
