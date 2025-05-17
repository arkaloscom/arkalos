from arkalos import Registry

from arkalos import Log, HTTP, base_path
from arkalos.http.middleware.handle_exceptions_middleware import HandleExceptionsMiddleware
from arkalos.http.middleware.log_requests_middleware import LogRequestsMiddleware



def register():
    #Registry.register()
    ...

def run():
    try:
        register()

        # Initialize the global logger configuration
        Log.logger()

        # Configure the HTTP API backend application
        app = (HTTP()
            .withBasePath(base_path())
            .withMiddleware([
                HandleExceptionsMiddleware,
                LogRequestsMiddleware,
            ])
            .withRoutes([
                ('app/http/routes', '/api')
            ])
            .withMountFrontendBuildDir()
            .create()
        )

        return app
    
    except Exception as e:
        Log.exception(e)
