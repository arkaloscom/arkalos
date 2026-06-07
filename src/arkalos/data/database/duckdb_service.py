
import duckdb
from typing import Any

from arkalos.data.database.db_service import DBService, DBWriteMessageType, DBReadMessageType



class DuckDBService(DBService):

    _connection: duckdb.DuckDBPyConnection|None
    _dbName: str

    def __init__(self, db_name: str):
        self._dbName = db_name
        self._connection = None

    def connect(self):
        self._connection = duckdb.connect(self._dbName)

    def disconnect(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def executeRead(self, sql: str, params: list|None = None) -> DBReadMessageType:
        if self._connection is None:
            raise RuntimeWarning('DuckDBService.executeRead(): Not connected.')
        if params:
            result = self._connection.execute(sql, params)
        else:
            result = self._connection.execute(sql)
        
        rows = result.fetchall()
        columns = [desc[0] for desc in result.description] if result.description else []
        row_data = [tuple(row) for row in rows]
        
        return DBReadMessageType(
            columns=columns,
            rows=row_data,
            row_count=len(row_data)
        )

    def executeWrite(self, sql: str, params: list|None = None) -> DBWriteMessageType:
        if self._connection is None:
            raise RuntimeWarning('DuckDBService.executeWrite(): Not connected.')
        if params:
            result = self._connection.execute(sql, params)
        else:
            result = self._connection.execute(sql)
            
        # DuckDB doesn't have rowcount/lastrowid like SQLite
        # For INSERT statements, query for the count
        rows_affected = 0  # DuckDB doesn't provide this directly
        last_insert_id = None  # DuckDB doesn't have auto-increment IDs by default
        
        return DBWriteMessageType(
            rows_affected=rows_affected,
            last_insert_id=last_insert_id
        )

    def commit(self):
        if self._connection is None:
            raise RuntimeWarning('DuckDBService.commit(): Not connected.')
        return self._connection.commit()
