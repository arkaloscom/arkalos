
import socketserver
import sqlite3
import struct
from typing import Any, Type
from enum import IntEnum
import pickle
import atexit

from arkalos.core.logger import log as Log
from arkalos.data.database.db_service import (
    DBService, 
    DBWriteMessageType, 
    DBReadMessageType, 
    DBErrorMessageType
)



class MessageType(IntEnum):
    """Message types for client-server communication"""
    QUERY = 1
    QUERY_RESULT = 2
    COMMAND_COMPLETE = 3
    ERROR = 4
    # COMMIT = 5
    # ROLLBACK = 6
    # BEGIN = 7



class DBRequestHandler(socketserver.BaseRequestHandler):
    """Handle individual client requests"""

    server: 'ThreadedTCPServer'
    service: DBService

    def __init__(self, request, client_address: tuple, server: 'ThreadedTCPServer'):
        self.service = server.service
        super().__init__(request, client_address, server)
    
    def setup(self) -> None:
        """Initialize connection-specific resources"""
        Log.debug(f'DBServer: Client connected: {self.client_address}')
    
    def handle(self) -> None:
        """Main request handling loop"""
        try:
            while True:
                message = self.receive_message()
                if not message:
                    break
                
                try:
                    # Deserialize the message
                    msg_type, data = self.deserialize_message(message)
                    
                    if msg_type == MessageType.QUERY:
                        self.handle_query(data)
                    else:
                        self.send_error("Unknown message type")
                        
                except Exception as e:
                    self.send_error(f"Message processing error: {str(e)}")
                    
        except ConnectionResetError:
            Log.debug(f'DBServer: Client connection reset: {self.client_address}')
        except Exception as e:
            Log.exception(e)
    
    def handle_query(self, query_data: dict[str, Any]) -> None:
        """Execute SQL query and send response"""
        try:
            response_data: DBReadMessageType|DBWriteMessageType
            sql = query_data.get('sql', '')
            params = query_data.get('params', [])
            
            Log.debug(f'DBServer: Executing SQL.', {'sql': sql[:100]})
            
            if sql.strip().upper().startswith(('SELECT', 'PRAGMA', 'EXPLAIN', 'DESCRIBE')):
                # Query that returns data
                response_data = self.service.executeRead(sql, params)
                self.send_message(MessageType.QUERY_RESULT, response_data)
            else:
                # DDL/DML query
                response_data = self.service.executeWrite(sql, params)
                self.send_message(MessageType.COMMAND_COMPLETE, response_data)
                
        except sqlite3.Error as e:
            self.send_error(f"SQL Error: {str(e)}")
    
    def send_message(self, 
        msg_type: MessageType,
        data: DBReadMessageType|DBWriteMessageType|DBErrorMessageType
    ):
        
        """Send a binary message to client"""
        # Serialize the data
        serialized_data = pickle.dumps(data)
        
        # Create message: [msg_type:1byte][data_length:4bytes][data:variable]
        message = struct.pack('!BI', msg_type, len(serialized_data)) + serialized_data
        
        # Send message length first, then message
        length_header = struct.pack('!I', len(message))
        self.request.sendall(length_header + message)
    
    def send_error(self, error_msg: str):
        """Send error message to client"""
        self.send_message(MessageType.ERROR, DBErrorMessageType(error=error_msg))
    
    def receive_message(self) -> bytes|None:
        """Receive a complete message from client"""
        # First, receive the message length (4 bytes)
        length_data = self.receive_exact(4)
        if not length_data:
            return None
            
        message_length = struct.unpack('!I', length_data)[0]
        
        # Then receive the actual message
        return self.receive_exact(message_length)
    
    def receive_exact(self, length: int) -> bytes|None:
        """Receive exactly 'length' bytes"""
        data = b''
        while len(data) < length:
            chunk = self.request.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def deserialize_message(self, message: bytes) -> tuple[MessageType, Any]:
        """Deserialize a binary message"""
        if len(message) < 5:  # minimum: 1 byte type + 4 byte length
            raise ValueError("DBServer: Message too short")
        
        # Extract message type and data length
        msg_type = MessageType(message[0])
        data_length = struct.unpack('!I', message[1:5])[0]
        
        # Extract and deserialize data
        data_bytes = message[5:5+data_length]
        data = pickle.loads(data_bytes)
        
        return msg_type, data
    
    def finish(self):
        """Clean up when client disconnects"""
        Log.debug(f'DBServer: Client disconnected: {self.client_address}')



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded SQLite server"""
    allow_reuse_address = True
    daemon_threads = True

    service: DBService

    def __init__(self, 
        server_address: tuple[str, int], 
        RequestHandlerClass: Type[socketserver.BaseRequestHandler], 
        service: DBService,
        bind_and_activate: bool = True,
    ):
        self.service = service
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)


class DBServer:

    NAME = 'DBServer'
    HOST = '127.0.0.1'
    PORT = 5555

    _server: ThreadedTCPServer|None
    _port: int
    service: DBService

    def __init__(self, service: DBService, port: int|None = None):
        self._server = None
        self.service = service
        self._port = port if port else self.PORT
        #self._setupCleanupHandlers()

    # def _setupCleanupHandlers(self):
    #     atexit.register(self.shutdown)

    def shutdown(self):
        """Gracefully shutdown the server"""
        if self._server:
            Log.debug(f'{self.NAME}: Shutting down server {self.HOST}:{self._port}.')
            self.onServerShutdown()
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def onServerStart(self):
        self.service.connect()

    def onServerShutdown(self):
        self.service.disconnect()

    def run(self, port: int|None = None):
        """Run the database server"""
        self._server = ThreadedTCPServer((self.HOST, self._port), DBRequestHandler, service=self.service)
        Log.debug(f'{self.NAME}: Starting server on {self.HOST}:{self._port}...')
        
        try:
            self.onServerStart()
            self._server.serve_forever()
        except:
            self.shutdown()

