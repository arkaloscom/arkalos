
import threading

from arkalos.data.database.db_client import DBClient
from arkalos.data.database.db_server import DBServer
from arkalos.data.database.db_service import DBService

class DBClerver(DBClient):

    _service: DBService
    _server: DBServer|None

    def __init__(self, service: DBService, port = None):
        self._server = None
        self._service = service
        super().__init__(port)

    def connect(self):
        if not self.isServerRunning():
            self.runBackgroundServer()
        super().connect()
    
    def disconnect(self):
        super().disconnect()
        if self._server:
            self._server.shutdown()
            self._server = None

    def runBackgroundServer(self):
        server_ready = threading.Event()
        
        def server_wrapper():
            self._server = DBServer(self._service, self._port)
            self._server.run()
            server_ready.set()
        
        server_thread = threading.Thread(target=server_wrapper, name='arkalos.dbclerver', daemon=True)
        server_thread.start()
        
        server_ready.wait(timeout=5)
