
import os
import importlib.util
import logging

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



class HTTPServer:

    __app: HTTPApp
    __router: APIRouter

    def __init__(self):
        self.__app = HTTPApp(
            title=config('app.name', 'Arkalos'),
            version=config('app.version', '0.0.0'),
            debug=False, 
            lifespan=self.lifespan)
        self.__router = APIRouter()

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

    def registerMiddlewares(self):
        middlewares = [
            HandleExceptionsMiddleware,
            LogRequestsMiddleware,
        ]
        for middleware in middlewares:
            self.__app.add_middleware(BaseHTTPMiddleware, dispatch=middleware())

    def mountDirs(self):
        # self.mountPublicDir()
        self.mountFrontendBuildDir()

    def mountPublicDir(self):
        self.__app.mount('/', StaticFiles(directory=base_path('public')), name='public')

    def mountFrontendBuildDir(self):
        self.__app.mount('/', SPAStaticFiles(directory=base_path('frontend/dist'), html=True), name='frontend')

    # Dynamically import and register all API route files from 'app/http/routes'.
    def registerRoutes(self):
        routers_dir = base_path(f'app/http/routes')
        for filename in os.listdir(routers_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"app.http.routes.{filename[:-3]}"
                module = importlib.import_module(module_name)
                if (hasattr(module, 'router')):
                    Log.info('Registering route file: ' + module_name)
                    self.__app.include_router(module.router, prefix='/api')

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
            bootstrap().run()

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
                'arkalos.http.server_start:app',
                host=host,
                port=port,
                reload=reload,
                reload_dirs=reload_dirs,
                reload_includes=reload_includes,
                workers=workers,
                log_config=Log.logger().getUvicornLogConfig(),
                access_log=False,
                log_level=logging.INFO
            )
        except BaseException as e:
            Log.exception(e)
