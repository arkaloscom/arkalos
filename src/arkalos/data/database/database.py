
from __future__ import annotations
from typing import TYPE_CHECKING, Type, Callable, overload, Literal
if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from contextlib import contextmanager
import re
from enum import StrEnum
import ibis # type: ignore
from pydantic import BaseModel
import polars as pl
import sqlite3
import duckdb

from arkalos.core.config import config
from arkalos.core.path import base_path
from arkalos.core.logger import log as Log
from arkalos.utils.str_utils import snake
from arkalos.schema.dml.insert_query_builder import InsertQueryBuilder
from arkalos.schema.dml.update_query_builder import UpdateQueryBuilder
from arkalos.schema.dml.delete_query_builder import DeleteQueryBuilder
from arkalos.schema.ddl.drop_table_builder import DropTableBuilder
from arkalos.schema.ddl.table_builder import TableBuilder
from arkalos.schema.ddl.sequence_builder import SequenceBuilder
from arkalos.schema.types.sql_type import SQL_TYPE
from arkalos.schema.types.data_input_type import (
    DataItemType,
    DataItemClassType,
    DataCollectionType,
    DataInputType,
    input_to_df,
    input_or_first_row_to_class
)


class DatabaseType(StrEnum):
    DATABASE = 'DB'
    DATA_WAREHOUSE = 'DWH'



class Database:

    TYPE: DatabaseType = DatabaseType.DATABASE

    _connection: ibis.BaseBackend|None
    _cursor: sqlite3.Cursor|duckdb.DuckDBPyConnection|None

    _engine: str
    _filePath: str
    _host: str
    _port: str
    _database: str
    _username: str
    _password: str



    def __init__(self) -> None:
        self._connection = None
        self._cursor = None
        self._engine = str(config('database.engine')).lower()
        self._host = str(config('database.host')).lower()
        self._port = str(config('database.port')).lower()
        self._database = str(config('database.database')).lower()
        self._username = str(config('database.username')).lower()
        self._password = str(config('database.password')).lower()
        self._filePath = str(config('database.path')).lower()



    def getIbisConnection(self):
        if self._connection is None:
            raise self._notConnectedError()
        return self._connection

    def isDatabase(self) -> bool:
        return self.TYPE == DatabaseType.DATABASE
    
    def isDataWarehouse(self) -> bool:
        return self.TYPE == DatabaseType.DATA_WAREHOUSE

    def getCredentialsLine(self) -> str:
        if self._engine in ('sqlite', 'duckdb'):
            return f'{self._engine}:///{base_path(self._filePath)}'

        return f'{self._engine}://{self._username}:{self._password}@{self._host}:{self._port}/{self._database}'
    
    def getEngineName(self) -> str:
        return self._engine
    
    def getDatabaseName(self) -> str:
        if self._engine in ('sqlite', 'duckdb'):
            return self._filePath
        return self._database
    
    def _logConnecting(self) -> None:
        type_msg = 'Data Warehouse' if self.isDataWarehouse() else 'Database'
        engine = self.getEngineName()
        db_name = self.getDatabaseName()
        Log.debug(f'Connecting to the {type_msg} | Engine: {engine} | DB Name: {db_name}')

    def _logDisconnecting(self) -> None:
        type_msg = 'Data Warehouse' if self.isDataWarehouse() else 'Database'
        engine = self.getEngineName()
        db_name = self.getDatabaseName()
        Log.debug(f'Disconnecting from the {type_msg} | Engine: {engine} | DB Name: {db_name}')
    
    def connect(self) -> None:
        creds = self.getCredentialsLine()
        if self._connection is None:
            self._logConnecting()
            self.onBeforeConnect()
            self._connection = ibis.connect(creds)
            self._cursor = self._connection.con.cursor()
            self.onAfterConnected()

    def disconnect(self) -> None:
        if self._connection is not None:
            self._logDisconnecting()
            self.onBeforeDisconnect()
            self._connection.disconnect()
            self.onAfterDisconnected()
            self._connection = None
            self._cursor = None

    def onBeforeConnect(self) -> None:
        pass

    def onAfterConnected(self) -> None:
        pass

    def onBeforeDisconnect(self) -> None:
        pass

    def onAfterDisconnected(self) -> None:
        pass

    def onSchemaUpdate(self, table_name: str, table_group: str|None = None) -> None:
        pass

    def _notConnectedError(self):
        return ValueError('executeSql(): Not connected to a database')
    


    ###########################################################################
    # STATS / DEBUG
    ###########################################################################
    
    def listTables(self, table_group: str|None = None) -> list[str]:
        if self._connection is None:
            raise self._notConnectedError()
        return self._connection.list_tables(database=table_group)
    
    def tableExists(self, table: str, table_group: str|None = None) -> bool:
        return table in self.listTables(table_group)
    
    def printTablesAndColumns(self, table_group: str|None = None) -> None:
        if self._connection is None:
            raise self._notConnectedError()
        tables = self.listTables(table_group)
        for table in tables:
            print(f"{self._connection.table(table)}")
            print()

    def showCreateTables(self, table_group: str|None = None) -> pl.DataFrame:
        if self._engine == 'sqlite':
            prefix = table_group + '.' if table_group else ''
            return self.executeSql(
                f"SELECT name, sql FROM {prefix}sqlite_master WHERE type='table'", 
                select=True
            )
        elif self._engine == 'duckdb':
            if table_group:
                return self.executeSql(
                    f"SELECT table_name AS name, sql FROM duckdb_tables WHERE schema_name='{table_group}'",
                    select=True
                )
            else:
                return self.executeSql("SELECT table_name AS name, sql FROM duckdb_tables", select=True)
        else:
            raise ValueError('Database.showCreateTables(): Engine is not supported.')

    def showCreateTable(self, table_name: str, table_group: str|None = None) -> str|None:
        df = self.showCreateTables(table_group)
        return df.filter(pl.col('name') == table_name).select('sql').item(0)
    
    def showCreateTablesAsDump(self, table_group: str|None = None) -> str:
        df = self.showCreateTables(table_group)
        res = '\n'
        for row in df.iter_rows(named=True):
            table_name = row['name']
            table_sql = row['sql']
            if self._engine == 'sqlite':
                prefix = table_group + '.' if table_group else ''
                res = res + table_sql.replace('TABLE ' + table_name, 'TABLE ' + prefix + table_name) + '\n\n'
            else:
                res = res + table_sql + '\n\n'
        return res


    ###########################################################################
    # RAW SQL
    ###########################################################################

    def _limitInsertSqlString(self, sql: str):
        pattern = r'(INSERT\s+INTO\s+.*?\s+VALUES\s*\([^)]*\))'
        match = re.search(pattern, sql, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1) + ", ..."
        return sql
    
    def _logQuery(self, sql: str) -> None:
        if not sql.startswith('ATTACH DATABASE') and not sql.startswith('CREATE SCHEMA'):
            Log.debug('Executing raw SQL', {'sql': self._limitInsertSqlString(sql)})

    @overload
    def executeSql(self, sql: str) -> None:
        ...

    @overload
    def executeSql(self, sql: str, select: Literal[True]) -> pl.DataFrame:
        ...

    def executeSql(self, sql: str, select: bool = False) -> pl.DataFrame|None:
        if self._connection is None:
            raise self._notConnectedError()
        if self._cursor is None:
            raise self._notConnectedError()
        
        self._logQuery(sql)

        self._cursor.execute(sql)
        df = None
        if select:
            if self._engine == 'sqlite' and isinstance(self._cursor, sqlite3.Cursor):
                column_names = [description[0] for description in self._cursor.description]
                rows = self._cursor.fetchall()
                data_for_polars = [tuple(row) for row in rows]
                if not data_for_polars:
                    df = pl.DataFrame({}, schema={name: pl.Object for name in column_names})
                else:
                    df = pl.DataFrame(data_for_polars, schema=column_names)
            elif self._engine == 'duckdb' and isinstance(self._cursor, duckdb.DuckDBPyConnection):
                return self._cursor.pl()
            else:
                raise RuntimeError("Database.executeSql(): Invalid cursor type")

        self._connection.con.commit()
        return df



    ###########################################################################
    # TABLE / DDL
    ###########################################################################

    def _isBool(self, pl_type: pl.DataType) -> bool:
        return isinstance(pl_type, (pl.Boolean))

    def _isInt(self, pl_type: pl.DataType) -> bool:
        return isinstance(pl_type, (pl.Int16, pl.Int32, pl.Int64, pl.Int128))
    
    def _isText(self, pl_type: pl.DataType) -> bool:
        return isinstance(pl_type, (pl.String))
    
    def _isDecimal(self, pl_type: pl.DataType) -> bool:
        return isinstance(pl_type, (pl.Float32, pl.Float64))
    
    def _isDatetime(self, pl_type: pl.DataType) -> bool:
        return isinstance(pl_type, (pl.Datetime))
    
    def _isDate(self, pl_type: pl.DataType) -> bool:
        return isinstance(pl_type, (pl.Date))
    
    def _isArray(self, pl_type: pl.DataType) -> bool:
        return isinstance(pl_type, (pl.Array, pl.List))
    
    def _isObject(self, pl_type: pl.DataType) -> bool:
        return isinstance(pl_type, (pl.Struct, pl.Object))
    
    def _boolColType(self):
        return SQL_TYPE.BOOLEAN

    def _intColType(self):
        return SQL_TYPE.INT
    
    def _textColType(self):
        return SQL_TYPE.TEXT
    
    def _decimalColType(self):
        return SQL_TYPE.DECIMAL
    
    def _dateTimeColType(self):
        return SQL_TYPE.DATETIME
    
    def _dateColType(self):
        return SQL_TYPE.DATE
    
    def _arrayColType(self):
        return SQL_TYPE.ARRAY
    
    def _objectColType(self):
        return SQL_TYPE.JSON    

    def _createColFromPolarsType(self, pl_type: pl.DataType, table: TableBuilder, norm_col_name: str):
        if self._isBool(pl_type):
            table.col(norm_col_name).type(self._boolColType())
        elif self._isInt(pl_type):
            table.col(norm_col_name).type(self._intColType())
        elif self._isDecimal(pl_type):
            table.col(norm_col_name).type(self._decimalColType())
        elif self._isText(pl_type):
            table.col(norm_col_name).type(self._textColType())
        elif self._isDatetime(pl_type):
            table.col(norm_col_name).type(self._dateTimeColType())
        elif self._isDate(pl_type):
            table.col(norm_col_name).type(self._dateColType())
        elif self._isArray(pl_type):
            table.col(norm_col_name).type(self._arrayColType())
        elif self._isObject(pl_type):
            table.col(norm_col_name).type(self._objectColType())
        else:
            # For any other type, create a text col
            table.col(norm_col_name).type(self._textColType())

    def autoCreateTable(self, table_name: str, schema: pl.Schema, table_group: str|None = None):
        with TableBuilder(table_name, table_group=table_group, dialect=self._engine) as table:
            for col_name in schema:
                pl_type = schema[col_name]
                norm_col_name = snake(col_name)
                self._createColFromPolarsType(pl_type, table, norm_col_name)

        sql = table.sql(dialect=self.getEngineName())
        self.executeSql(sql)
        self.onSchemaUpdate(table_name, table_group)

    @contextmanager
    def createTable(self, table_name: str, table_group: str|None = None):
        builder = TableBuilder(table_name, table_group=table_group, dialect=self._engine)
        yield builder
        sql = builder.sql(dialect=self.getEngineName())
        if builder.hasIdCol() and self._engine == 'duckdb':
            seq_sql = SequenceBuilder(table_name, table_group).sql(dialect=self._engine)
            self.executeSql(seq_sql)
        self.executeSql(sql)
        if not table_name.startswith('_'):
            self.onSchemaUpdate(table_name, table_group)

    @contextmanager
    def alterTable(self, table_name: str, table_group: str|None = None):
        builder = TableBuilder(table_name, table_group=table_group, alter=True, dialect=self._engine)
        yield builder
        sql = builder.sql(dialect=self.getEngineName())
        if builder.hasIdCol() and self._engine == 'duckdb':
            seq_sql = SequenceBuilder(table_name, table_group).sql(dialect=self._engine)
            self.executeSql(seq_sql)
        self.executeSql(sql)
        self.onSchemaUpdate(table_name, table_group)

    def dropTable(self, table_name: str, table_group: str|None = None):
        sql = DropTableBuilder(table_name, table_group).sql(dialect=self.getEngineName())
        self.executeSql(sql)
        self.onSchemaUpdate(table_name, table_group)



    ###########################################################################
    # INSERT / CREATE
    ###########################################################################

    def insert(self, table_name: str, item: DataItemType, table_group: str|None = None) -> None:
        if self._connection is None:
            raise self._notConnectedError()
        sql = (InsertQueryBuilder(table_name, table_group)
            .insert(item)
            .sql(dialect=self.getEngineName())
        )
        self.executeSql(sql)

    def insertReturning(self, 
        table_name: str, 
        item: DataItemType, 
        cls: DataItemClassType|None = None,
        table_group: str|None = None
    ) -> DataItemType:
        
        if self._connection is None:
            raise self._notConnectedError()
        
        if cls is None:
            cls = type(item)

        self.insert(table_name, item, table_group=table_group)
        table = self._connection.table(table_name, database=table_group)
        df = table.filter(table.id == table.id.max()).to_polars()
        return input_or_first_row_to_class(df, cls)
    
    def insertMultiple(self, 
        table_name: str, 
        data: DataCollectionType, 
        table_group: str|None = None
    ) -> None:
        if self._connection is None:
            raise self._notConnectedError()
        sql = (InsertQueryBuilder(table_name, table_group)
            .insertMultiple(data)
            .sql(dialect=self.getEngineName())
        )
        self.executeSql(sql)



    ###########################################################################
    # SELECT / READ
    ###########################################################################

    def table(self, table_name: str, table_group: str|None = None) -> ibis.Table:
        if self._connection is None:
            raise self._notConnectedError()
        return self._connection.table(table_name, database=table_group)
    
    def selectAll(self, table_name: str, table_group: str|None = None) -> pl.DataFrame:
        return pl.from_pandas(self.table(table_name, table_group).execute())
    


    ###########################################################################
    # UPDATE
    ###########################################################################

    def update(self, 
        table_name, 
        item: DataItemType, where_col: str, 
        where_val: str|int,
        table_group: str|None = None
    ):
        sql = (UpdateQueryBuilder(table_name, table_group)
            .update(item)
            .where(where_col, where_val)
            .sql(dialect=self.getEngineName())
        )
        return self.executeSql(sql)


    ###########################################################################
    # DELETE
    ###########################################################################

    def delete(self, table_name: str, where_col: str, where_val: str, table_group: str|None = None):
        sql = (DeleteQueryBuilder(table_name, table_group)
            .where(where_col, where_val)
            .sql(dialect=self.getEngineName())
        )
        return self.executeSql(sql)
