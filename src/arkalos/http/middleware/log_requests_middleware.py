
from typing import Callable
import http
import time

from arkalos.core.logger import log as Log
from arkalos.http.request import Request
from arkalos.http.response import Response
from arkalos.http.middleware.middleware import Middleware



class LogRequestsMiddleware(Middleware):

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        url = f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
        start_time = time.time()

        resp = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)
        server_info = request.scope.get("server")
        host = server_info[0] if server_info else 'NULL'
        port = server_info[1] if server_info else 'NULL'

        try:
            status_phrase = http.HTTPStatus(resp.status_code).phrase
        except ValueError:
            status_phrase=""

        ip = request.client.host if request.client else 'NULL'
        Log.access(f'"{request.method} {url}" {resp.status_code} {status_phrase}', {
            'client': ip,
            'server': f'{host}:{port}'
        })
        return resp
    