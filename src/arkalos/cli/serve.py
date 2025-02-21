from arkalos.core.http import http_server
from arkalos.core.bootstrap import bootstrap

def run():
    bootstrap().run()
    server = http_server()
    server.run()
