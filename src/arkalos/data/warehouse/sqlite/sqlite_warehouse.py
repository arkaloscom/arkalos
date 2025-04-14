import sqlite3

from arkalos.core.config import config
from arkalos.data.extractors.data_extractor import TabularDataExtractor
from arkalos.data.warehouse.data_warehouse import DataWarehouse

class SQLiteWarehouse(DataWarehouse):

    NAME = 'SQLite'
    DESCRIPTION = 'Simple SQLite data warehouse'

    DTYPE_INT = 'INTEGER'
    DTYPE_FLOAT = 'REAL'
    DTYPE_TEXT = 'TEXT'
    DTYPE_BOOL = 'NUMERIC'
    DTYPE_DATETIME = 'TEXT'
    DTYPE_ARRAY = 'TEXT'
    DTYPE_JSON = 'TEXT'

    __path = config('data_warehouse.path', 'data/dwh/dwh.db')

    _connection: sqlite3.Connection
    _cursor: sqlite3.Cursor



    def connect(self):
        if (self._connection is None):
            self._connection = sqlite3.connect(self.__path)
            self._cursor = self._connection.cursor()

    def generateCreateSchemaQuery(self, extractor: TabularDataExtractor, table_name: str, data_schema: dict) -> str:
        columns = []
        for column, dtype in data_schema.items():
            sqlite_type = self.mapDataType(dtype)
            columns.append(f'"{column}" {sqlite_type}')
        columns_sql = ",\n  ".join(columns)
        return f"CREATE TABLE {self.generateTableName(extractor, table_name)} (\n  {columns_sql}\n);"
    
    def generateDropSchemaQuery(self, extractor: TabularDataExtractor, table_name: str) -> str:
        drop_table_sql = f"DROP TABLE IF EXISTS {self.generateTableName(extractor, table_name)};"
        return drop_table_sql

    def generateInsertQuery(self, serialized_row, extractor: TabularDataExtractor, table_name: str) -> str:
        columns = ", ".join(f'"{col}"' for col in serialized_row.keys())
        placeholders = ", ".join("?" for _ in serialized_row.values())
        insert_sql = f"INSERT INTO {self.generateTableName(extractor, table_name)} ({columns}) VALUES ({placeholders})"
        return insert_sql   

    def generateUpdateQuery(self, serialized_row, extractor: TabularDataExtractor, table_name: str, id) -> str:
        set_values = ", ".join([f'"{col}" = ?' for col in serialized_row.keys()])
        update_sql = f"UPDATE {self.generateTableName(extractor, table_name)} SET {set_values} WHERE id = ?"
        return update_sql

    def executeQuery(self, query: str, values = ()):
        self._cursor.execute(query, values)
        self._connection.commit()

    def selectQuery(self, query: str, values = ()) -> tuple:
        self._cursor.execute(query, values)
        results = (self._cursor.fetchall(), self._cursor.description)
        return results
    