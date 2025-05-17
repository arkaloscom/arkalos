
import os
import importlib.util
import logging
from typing import Type

from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from arkalos.core.bootstrap import bootstrap
from arkalos.core.config import config
from arkalos.core.path import base_path
from arkalos.core.logger import log as Log
from arkalos.core.dwh import dwh

from arkalos.http.app import HTTPApp
from arkalos.http.response import response
from arkalos.http.middleware.middleware import BaseHTTPMiddleware
from arkalos.http.middleware.handle_exceptions_middleware import HandleExceptionsMiddleware
from arkalos.http.middleware.log_requests_middleware import LogRequestsMiddleware
from arkalos.http.spa_static_files import SPAStaticFiles
from arkalos.http.middleware.middleware import Middleware



class HTTPServer:

    __app: HTTPApp
    __router: APIRouter

    __base_path: str
    __middleware: list[Type[Middleware]]
    __route_dirs: list[tuple[str, str]]

    def __init__(self):
        self.__app = HTTPApp(
            title=config('app.name', 'Arkalos'),
            version=config('app.version', '0.0.0'),
            debug=False, 
            lifespan=self.lifespan)
        self.__router = APIRouter()

    def withBasePath(self, base_path: str) -> 'HTTPServer':
        self.__base_path = base_path
        Log.debug('Application base path is: ' + self.__base_path)
        return self

    def registerExceptionHandlers(self):
        # self.__app.add_exception_handler(RequestValidationError, self._validationExceptionHandler)
        # self.__app.add_exception_handler(HTTPException, self._HTTPExceptionHandler)
        # self.__app.add_exception_handler(Exception, None)
        pass

    async def _validationExceptionHandler(self, request, exc):
        return response({"error": str(exc)}, 422)
    
    async def _HTTPExceptionHandler(self, request, exc):
        Log.error(f"HTTP error {exc.status_code}: {exc.detail}")
        return response({"error": exc.detail}, exc.status_code)
    
    async def _genericExceptionHandler(self, request, exc):
        pass

    def withMiddleware(self, middleware: list[Type[Middleware]]) -> 'HTTPServer':
        self.__middleware = middleware
        self.registerMiddlewares()
        return self

    def registerMiddlewares(self):
        for middleware in self.__middleware:
            Log.debug('Registering middleware: ' + middleware.__module__)
            self.__app.add_middleware(BaseHTTPMiddleware, dispatch=middleware())

    # def mountDirs(self):
    #     # self.mountPublicDir()
    #     self.mountFrontendBuildDir()

    # def mountPublicDir(self):
    #     self.__app.mount('/', StaticFiles(directory=base_path('public')), name='public')

    def withMountFrontendBuildDir(self) -> 'HTTPServer':
        path = base_path('frontend/dist')
        if os.path.exists(path):
            Log.debug('Mounting static files (Frontend build directory): frontend/dist')
            self.__app.mount('/', SPAStaticFiles(directory=base_path('frontend/dist'), html=True), name='frontend')
        else:
            Log.warning('Bootstrapping the HTTP application with frontend build direcotry, ' \
            'but directory "frontend/dist" doesn\'t exist. Do "cd frontend && npm run build" '
            'or disable mounting frontend build dir in the app/bootstrap.py.')
        return self

    def withRoutes(self, route_dirs: list[tuple[str, str]]) -> 'HTTPServer':
        self.__route_dirs = route_dirs
        self.registerRoutes()
        return self

    def registerRoutes(self):
        for route_dir in self.__route_dirs:
            dir = route_dir[0]
            prefix = route_dir[1]
            self.registerRoutesDir(dir, prefix)

    # Dynamically import and register all route files from the dir
    def registerRoutesDir(self, dir='app/http/routes', prefix='/api'):
        routers_dir = base_path(dir)
        for filename in os.listdir(routers_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_path = dir.strip('/').replace('/', '.')
                module_name = f'{module_path}.{filename[:-3]}'
                module = importlib.import_module(module_name)
                if (hasattr(module, 'router')):
                    Log.debug('Registering route file: ' + module_name)
                    self.__app.include_router(module.router, prefix=prefix)

    def create(self):
        return self.__app

    def getApp(self):
        return self.__app

    def getRouter(self):
        return self.__router
    
    async def lifespan(self, app: FastAPI):
        self.onServerStart()
        yield  # Server runs during this time
        self.onServerStop()

    def onServerStart(self):
        dwh().connect()

    def onServerStop(self):
        dwh().disconnect()

    def run(self, host: str = '127.0.0.1', port: int = 8000, reload: bool = False, workers: int = 1):
        try:
            bootstrap().register()
            Log.logger()

            reload_includes: list[str]|None = None
            reload_dirs: list[str]|None = None
            if reload:
                reload_dirs = [
                    'app',
                    'config'
                ]
                reload_includes = [
                    '.env'
                ]

            Log.info(f"Starting Arkalos HTTP server (App name: '{config('app.name', '')}') (App env: '{config('app.env', '')}')...")
            Log.info(f"Config: host={host}, port={port}, workers={workers}, reload={reload}")

            uvicorn.run(
                'app.bootstrap:run',
                host=host,
                port=port,
                reload=reload,
                reload_dirs=reload_dirs,
                reload_includes=reload_includes,
                workers=workers,
                log_config=Log.logger().getUvicornLogConfig(),
                access_log=False,
                log_level=logging.INFO,
                factory=True
            )
        except BaseException as e:
            Log.exception(e)
