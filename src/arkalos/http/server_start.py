
from arkalos.core.logger import log as Log
from arkalos.core.bootstrap import bootstrap
from arkalos.core.http import http_server

try:
    bootstrap().run()

    Log.logger()

    server = http_server()

    app = server.getApp()
    
    server.registerExceptionHandlers()
    server.registerMiddlewares()
    server.registerRoutes()
    server.mountDirs()

except BaseException as e:
    Log.exception(e)
