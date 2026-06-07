
import struct
from typing import Any, TypeGuard
import pickle
import socket
import atexit

import pandas as pd
import polars as pl
import pyarrow as pa # type: ignore

from arkalos.data.database.db_server import MessageType
from arkalos.data.database.db_service import DBReadMessageType, DBWriteMessageType, DBErrorMessageType



class DBCursor:
    """Cursor-like object that provides fetchall, fetchone, fetch_arrow_table methods"""
    
    _result: DBReadMessageType|DBWriteMessageType
    _current_row: int

    def __init__(self, result: DBReadMessageType|DBWriteMessageType):
        self._result = result
        self._current_row = 0
        
    def fetchall(self) -> list[tuple]:
        """Return all remaining rows as a list of tuples"""
        if isinstance(self._result, DBReadMessageType):
            return [tuple(row) for row in self._result.rows[self._current_row:]]
        return []
    
    def fetchone(self) -> tuple|None:
        """Return the next row as a tuple, or None if no more rows"""
        if isinstance(self._result, DBReadMessageType) and self._current_row < len(self._result.rows):
            row = tuple(self._result.rows[self._current_row])
            self._current_row += 1
            return row
        return None
    
    def fetchmany(self, size: int = 1) -> list[tuple]:
        """Return up to 'size' rows as a list of tuples"""
        if isinstance(self._result, DBReadMessageType):
            start = self._current_row
            end = min(start + size, len(self._result.rows))
            self._current_row = end
            return [tuple(row) for row in self._result.rows[start:end]]
        return []
    
    def fetch_arrow_table(self) -> pa.Table:
        """Return results as PyArrow Table"""
        if isinstance(self._result, DBReadMessageType):
            # Convert to PyArrow Table
            data_dict = {}
            for i, column in enumerate(self._result.columns):
                data_dict[column] = [row[i] for row in self._result.rows]
            return pa.table(data_dict)
        else:
            # Return empty table for write operations
            return pa.table({})
        
    def arrow(self) -> pa.Table:
        return self.fetch_arrow_table()
    
    def fetch_df(self):
        """Return results as pandas DataFrame (requires pandas)"""
        if isinstance(self._result, DBReadMessageType):
            return pd.DataFrame(self._result.rows, columns=self._result.columns)
        else:
            return pd.DataFrame()
        
    def pd(self):
        return self.fetch_df()
    
    def df(self):
        return self.fetch_df()
        
    def pl(self):
        return pl.from_arrow(self.arrow())
    
    @property
    def columns(self) -> list[str]:
        """Return column names"""
        if isinstance(self._result, DBReadMessageType):
            return self._result.columns
        return []
    
    @property
    def rowcount(self) -> int:
        """Return number of rows affected/returned"""
        if isinstance(self._result, DBReadMessageType):
            return self._result.row_count
        else:
            return self._result.rows_affected
    
    @property
    def lastrowid(self) -> int|None:
        """Return last insert ID"""
        if isinstance(self._result, DBWriteMessageType):
            return self._result.last_insert_id
        return None
    
    def __iter__(self):
        """Make cursor iterable"""
        return self
    
    def __next__(self):
        """Iterator protocol"""
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row



class DBClient:
    """Binary protocol client for DBServer"""

    NAME = 'DBClient'
    HOST = '127.0.0.1'
    PORT = 5555

    _port: int
    _socket: socket.socket|None
    
    def __init__(self, port: int|None = None):
        self._port = port if port else self.PORT
        self._socket = None
        self._setupCleanupHandlers()

    def _setupCleanupHandlers(self):
        atexit.register(self.disconnect)

    def isServerRunning(self):
        sock = socket.socket()
        sock.settimeout(0.2)
        result = sock.connect_ex((self.HOST, self._port))
        sock.close()
        return result == 0
        
    def connect(self) -> 'DBClient':
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(10)
        self._socket.connect((self.HOST, self._port))
        return self
    
    def execute(self, sql: str, params: list|None = None) -> DBCursor:
        if not self._socket:
            raise Exception("Not connected to server")
            
        if params is None:
            params = []
        
        query_data = {'sql': sql, 'params': params}
        self._sendMessage(MessageType.QUERY, query_data)
        response = self._receiveMessage()
        return DBCursor(response)
    
    def sql(self, sql: str, params: list|None = None) -> DBCursor:
        return self.execute(sql, params)

    
    def _sendMessage(self, msg_type: MessageType, data: Any):
        """Send a binary message to server"""
        if not self._socket:
            raise Exception("Not connected to server")

        # Serialize the data
        serialized_data = pickle.dumps(data)
        
        # Create message: [msg_type:1byte][data_length:4bytes][data:variable]
        message = struct.pack('!BI', msg_type, len(serialized_data)) + serialized_data
        
        # Send message length first, then message
        length_header = struct.pack('!I', len(message))
        self._socket.sendall(length_header + message)
    
    def _receiveMessage(self) -> DBReadMessageType|DBWriteMessageType:
        """Receive and parse response from server"""
        # First, receive the message length
        length_data = self._receiveExact(4)
        if not length_data:
            raise ConnectionError("Server disconnected")
            
        message_length = struct.unpack('!I', length_data)[0]
        
        # Then receive the actual message
        message = self._receiveExact(message_length)
        
        # Parse message
        msg_type = MessageType(message[0])
        data_length = struct.unpack('!I', message[1:5])[0]
        data_bytes = message[5:5+data_length]
        data: DBReadMessageType|DBWriteMessageType|DBErrorMessageType = pickle.loads(data_bytes)
        
        # Handle different response types
        if msg_type == MessageType.ERROR:
            raise Exception(f"Server error: {data.error}") # type: ignore
        elif msg_type == MessageType.QUERY_RESULT:
            return data # type: ignore
        elif msg_type == MessageType.COMMAND_COMPLETE:
            return data # type: ignore
        else:
            raise Exception(f"Unknown response type: {msg_type}")
    
    def _receiveExact(self, length: int) -> bytes:
        """Receive exactly 'length' bytes"""
        if not self._socket:
            raise Exception("Not connected to server")
        data = b''
        while len(data) < length:
            chunk = self._socket.recv(length - len(data))
            if not chunk:
                raise ConnectionError("Connection lost")
            data += chunk
        return data
    
    def disconnect(self):
        """Close connection"""
        if self._socket:
            self._socket.close()
            self._socket = None

    def close(self):
        """Alias for disconnect() to match DuckDB API"""
        self.disconnect()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
