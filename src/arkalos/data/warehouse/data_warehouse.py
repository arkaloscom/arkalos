
from typing import Any
from abc import ABC, abstractmethod
import os
import json
import re
from datetime import datetime, timezone

import polars as pl

from arkalos.utils.schema import get_data_schema
from arkalos.data.extractors.data_extractor import TabularDataExtractor
from arkalos.core.config import config

class DataWarehouse(ABC):

    DTYPE_INT = 'INTEGER'
    DTYPE_FLOAT = 'REAL'
    DTYPE_TEXT = 'TEXT'
    DTYPE_BOOL = 'NUMERIC'
    DTYPE_DATETIME = 'TEXT'
    DTYPE_ARRAY = 'TEXT'
    DTYPE_JSON = 'TEXT'

    _connection: Any|None = None
    _cursor: Any|None = None

    NAME: str
    DESCRIPTION: str

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def generateCreateSchemaQuery(self, extractor: TabularDataExtractor, table_name: str, data_schema: dict) -> str:
        pass
    
    @abstractmethod
    def generateDropSchemaQuery(self, extractor: TabularDataExtractor, table_name: str) -> str:
        pass

    @abstractmethod
    def generateInsertQuery(self, serialized_row, extractor: TabularDataExtractor, table_name: str) -> str:
        pass

    @abstractmethod
    def generateUpdateQuery(self, serialized_row, extractor: TabularDataExtractor, table_name: str, id) -> str:
        pass

    @abstractmethod
    def executeQuery(self, query: str, values = None):
        pass

    @abstractmethod
    def selectQuery(self, query: str, values = None) -> tuple:
        pass



    def disconnect(self):
        if (self._connection is not None):
            self._connection.close()
            self._connection = None
            self._cursor = None


    def mapInt(self, polars_data_type: pl.Struct):
        if polars_data_type in (pl.Int64, pl.Int32, pl.Int16):
            return self.DTYPE_INT
        return False
    
    def mapFloat(self, polars_data_type: pl.Struct):
        if polars_data_type in (pl.Float64, pl.Float32):
            return self.DTYPE_FLOAT
        return False
    
    def mapText(self, polars_data_type: pl.Struct):
        if polars_data_type == pl.Utf8:
            return self.DTYPE_TEXT
        return False
    
    def mapBool(self, polars_data_type: pl.Struct):
        if polars_data_type == pl.Boolean:
            return self.DTYPE_BOOL
        return False
    
    def mapDatetime(self, polars_data_type: pl.Struct):
        if polars_data_type == pl.Datetime:
            return self.DTYPE_DATETIME
        return False
    
    def mapArray(self, polars_data_type: pl.Struct):
        if isinstance(polars_data_type, pl.List):
            return self.DTYPE_ARRAY
        return False
    
    def mapJSON(self, polars_data_type: pl.Struct):
        if isinstance(polars_data_type, pl.Struct):
            return self.DTYPE_JSON
        return False

    def mapDataType(self, polars_data_type: pl.Struct) -> str:
        mappers = [
            self.mapInt,
            self.mapFloat,
            self.mapText,
            self.mapBool,
            self.mapDatetime,
            self.mapArray,
            self.mapJSON
        ]
        for mapper in mappers:
            if col_type := mapper(polars_data_type):
                return col_type
        raise ValueError(f"Unsupported Polars type: {polars_data_type}")
    
    def detectDataSchema(self, data: pl.DataFrame) -> dict:
        return get_data_schema(data)
     
    def generateTableName(self, extractor: TabularDataExtractor, table_name: str) -> str:
        return extractor.NAME + '__' + table_name
        
    def dropTable(self, extractor: TabularDataExtractor, table_name: str):
        drop_table_sql = self.generateDropSchemaQuery(extractor, table_name)
        self.executeQuery(drop_table_sql)

    def createTable(self, extractor: TabularDataExtractor, table_name: str, data_schema: dict):
        create_table_sql = self.generateCreateSchemaQuery(extractor, table_name, data_schema)
        self.updateSchemaDefinitions(create_table_sql)
        self.executeQuery(create_table_sql)

    def serializeValue(self, value, dtype):
        if isinstance(dtype, pl.List) or isinstance(dtype, pl.Struct):
            return json.dumps(value)  # Serialize lists and structs as JSON
        elif dtype == pl.Datetime:
            return str(value)  # Store datetime as full string
        else:
            return value

    def serializeRow(self, row, data_schema):
        serialized_row = {col: self.serializeValue(row[col], data_schema[col]) for col in row}
        return serialized_row

    def importData(self, extractor: TabularDataExtractor, table_name: str, data_schema, data):
        for row in data:
            serialized_row = self.serializeRow(row, data_schema)
            insert_sql = self.generateInsertQuery(serialized_row, extractor, table_name)
            self.executeQuery(insert_sql, list(serialized_row.values()))

    def importUpdatedRow(self, extractor: TabularDataExtractor, table_name: str, data_schema, row, id):
        serialized_row = self.serializeRow(row, data_schema)
        update_sql = self.generateUpdateQuery(serialized_row, extractor, table_name, id)
        values = list(serialized_row.values()) + [id]
        self.executeQuery(update_sql, values)

    def updateLastSyncDate(self) -> None:
        # Write current UTC time to txt file
        with open('data/dwh/last_sync_date.txt', 'w') as f:
            f.write(datetime.now(timezone.utc).isoformat())
            # f.write(airtable_date_string.rstrip('Z'))

    def getLastSyncDate(self) -> str|None:
        try:
            with open('data/dwh/last_sync_date.txt', 'r') as f:
                return str(datetime.fromisoformat(f.read().strip()))
        except (FileNotFoundError, ValueError):
            return None
        
    def updateSchemaDefinitions(self, create_table_sql) -> None:
        schema_path = config('data_warehouse.schema_path')
        table_name_match = re.search(r'CREATE TABLE (IF NOT EXISTS )?(\w+)', create_table_sql, re.IGNORECASE)
        
        if not table_name_match:
            raise ValueError("Invalid CREATE TABLE statement.")
        
        table_name = table_name_match.group(2)
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_content = f.read()
        else:
            schema_content = ""
        
        table_pattern = re.compile(rf'CREATE TABLE (IF NOT EXISTS )?{table_name} .*?;', re.DOTALL | re.IGNORECASE)
        
        if table_pattern.search(schema_content):
            schema_content = table_pattern.sub(create_table_sql.strip() + ';', schema_content)
        else:
            schema_content += '\n\n' + create_table_sql.strip() + ';'
        
        with open(schema_path, 'w') as f:
            f.write(schema_content)

    def getSchemaDefinitions(self) -> str|None:
        try:
            with open(config('data_warehouse.schema_path'), 'r') as f:
                return f.read()
        except (FileNotFoundError, ValueError):
            return None
    