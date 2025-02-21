import os
import importlib.util

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from arkalos.core.path import base_path
from arkalos import dwh



class HTTPServer:

    __app = None
    __router = None

    def __init__(self):
        self.__app = FastAPI(lifespan=self.lifespan)
        self.__router = APIRouter()
        
    def registerMiddlewares(self):
        pass

    def mountPublicDir(self):
        self.__app.mount('/', StaticFiles(directory=base_path('public')), name='public')

    # Dynamically import and register web and API route files in 'app/http/routes'.
    def registerRoutes(self):
        routes = {
            "web": "",
            "api": "/api"
        }

        for route_type, prefix in routes.items():
            module_path = base_path(f"app/http/routes/{route_type}.py")
            module_name = f"app.http.routes.{route_type}"

            if not os.path.exists(module_path):
                print(f"⚠️ Route file '{module_path}' not found.")
                return

            # Dynamically import module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "router"):
                # Wrap web routes to always return HTMLResponse
                if route_type == "web":
                    for route in module.router.routes:
                        route.response_class = HTMLResponse

                self.__app.include_router(module.router, prefix=prefix)

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

    def run(self, host="127.0.0.1", port=8000, reload=False):
        self.registerMiddlewares()
        self.registerRoutes()
        self.mountPublicDir()
        uvicorn.run(self.__app, host=host, port=port, reload=reload)
