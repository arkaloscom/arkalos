
import sqlite3
from typing import Any

from arkalos.data.database.db_service import DBService, DBWriteMessageType, DBReadMessageType



class SQLiteService(DBService):

    _connection: sqlite3.Connection
    _dbName: str

    def __init__(self, db_name: str):
        self._dbName = db_name

    def connect(self):
        self._connection = sqlite3.connect(self._dbName, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row

    def disconnect(self):
        self._connection.close()

    def executeRead(self, sql: str, params: list|None = None) -> DBReadMessageType:
        cursor = self._connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        row_data = [tuple(row) for row in rows]
        return DBReadMessageType(
            columns = columns,
            rows = row_data,
            row_count = len(row_data)
        )

    def executeWrite(self, sql: str, params: list|None = None) -> DBWriteMessageType:
        cursor = self._connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        self._connection.commit()
        return DBWriteMessageType(
            rows_affected = cursor.rowcount,
            last_insert_id = cursor.lastrowid
        )
