
from __future__ import annotations
from typing import Type
from contextlib import contextmanager
from dataclasses import dataclass
import os
import re
from enum import StrEnum
from datetime import datetime, timezone

import polars as pl
import ibis # type: ignore

from arkalos.core.path import base_path
from arkalos.core.config import config
from arkalos.core.logger import log as Log
from arkalos.utils.str_utils import snake
from arkalos.data.extractors.data_extractor import TabularDataExtractor
from arkalos.data.database.database import Database, DatabaseType
from arkalos.schema.ddl.table_builder import TableBuilder
from arkalos.schema.types.data_input_type import DataItemType, DataItemClassType, DataCollectionType



@dataclass
class MetaRecordType:
    key: str
    val_str: str|None = None
    val_int: int|None = None
    val_datetime: datetime|None = None



class DataWarehouseLayerScope:

    _dwh: DataWarehouse
    _layerName: str



    def __init__(self, dwh: DataWarehouse, layer_name: str):
        self._dwh = dwh
        self._layerName = layer_name
        


    def layerName(self) -> str:
        return self._layerName
    
    # Stats
    
    def tableExists(self, table_name: str) -> bool:
        return self._dwh.tableExists(table_name, self.layerName())
    
    def listTables(self):
        return self._dwh.listTables(self.layerName())
    
    # DDL

    def autoCreateTable(self, table_name: str, schema: pl.Schema):
        sql = self._dwh.autoCreateTable(table_name, schema, self.layerName())
        self._dwh.schemaUpdateDump(self._layerName)

    def _onCreateTableSuccess(self, sql: str):
        self._dwh.schemaUpdateDump(self._layerName)

    def createTable(self, table_name: str):
        return self._dwh.createTable(table_name, self.layerName())

    def alterTable(self, table_name: str):
        return self._dwh.alterTable(table_name, self.layerName())
    
    def dropTable(self, table_name: str):
        return self._dwh.dropTable(table_name, self.layerName())
    
    # Select
    
    def table(self, table_name: str) -> ibis.Table:
        return self._dwh.table(table_name, self.layerName())
    
    def selectAll(self, table_name: str) -> pl.DataFrame:
        return self._dwh.selectAll(table_name, table_group=self.layerName())
    
    # Insert
    
    def insert(self, table_name: str, item: DataItemType) -> None:
        return self._dwh.insert(table_name, item, table_group=self.layerName())
    
    def insertReturning(self, 
        table_name: str, 
        item: DataItemType,
        cls: DataItemClassType|None = None
    ) -> DataItemType:
        return self._dwh.insertReturning(table_name, item, cls, table_group=self.layerName())
    
    def insertMultiple(self, table_name: str, data: DataCollectionType) -> None:
        return self._dwh.insertMultiple(table_name, data, table_group=self.layerName())
    
    # Update
    
    def update(self, table_name: str, item: DataItemType, where_col: str, where_val: str|int):
        return self._dwh.update(table_name, item, where_col, where_val, table_group=self.layerName())
    
    # Delete
    
    def delete(self, table_name: str, where_col: str, where_val: str):
        return self._dwh.delete(table_name, where_col, where_val, table_group=self.layerName())



class DataWarehouse(Database):

    TYPE: DatabaseType = DatabaseType.DATA_WAREHOUSE
    META_TABLE_NAME: str = '_meta'

    _sqliteRawPath: str
    _sqliteCleanPath: str
    _sqliteBIPath: str

    _schemaFilePathRaw: str
    _schemaFilePathClean: str
    _schemaFilePathBI: str

    _rawLayerName: str
    _cleanLayerName: str
    _BILayerName: str

    _rawLayerScope: DataWarehouseLayerScope
    _cleanLayerScope: DataWarehouseLayerScope
    _BILayerScope: DataWarehouseLayerScope

    def __init__(self) -> None:
        self._connection = None
        self._engine = str(config('data_warehouse.engine')).lower()
        self._host = str(config('data_warehouse.host')).lower()
        self._port = str(config('data_warehouse.port')).lower()
        self._database = str(config('data_warehouse.database')).lower()
        self._username = str(config('data_warehouse.username')).lower()
        self._password = str(config('data_warehouse.password')).lower()

        suffix = '_ddb' if self._engine == 'duckdb' else ''
        self._filePath = str(config(f'data_warehouse.path{suffix}')).lower()

        self._sqliteRawPath = str(config('data_warehouse.path_raw')).lower()
        self._sqliteCleanPath = str(config('data_warehouse.path_clean')).lower()
        self._sqliteBIPath = str(config('data_warehouse.path_bi')).lower()

        self._schemaFilePathRaw = str(config('data_warehouse.schema_path_raw')).lower()
        self._schemaFilePathClean = str(config('data_warehouse.schema_path_clean')).lower()
        self._schemaFilePathBI = str(config('data_warehouse.schema_path_bi')).lower()

        self._rawLayerName = str(config('data_warehouse.layer_raw')).lower()
        self._cleanLayerName = str(config('data_warehouse.layer_clean')).lower()
        self._BILayerName = str(config('data_warehouse.layer_bi')).lower()

        self._rawLayerScope = DataWarehouseLayerScope(self, self._rawLayerName)
        self._cleanLayerScope = DataWarehouseLayerScope(self, self._cleanLayerName)
        self._BILayerScope = DataWarehouseLayerScope(self, self._BILayerName)


    def onAfterConnected(self) -> None:
        if self._engine == 'sqlite':
            self.executeSql(f"ATTACH DATABASE '{base_path(self._sqliteRawPath)}' AS {self.raw().layerName()}")
            self.executeSql(f"ATTACH DATABASE '{base_path(self._sqliteCleanPath)}' AS {self.clean().layerName()}")
            self.executeSql(f"ATTACH DATABASE '{base_path(self._sqliteBIPath)}' AS {self.BI().layerName()}")
        elif self._engine == 'duckdb':
            self.executeSql(f'CREATE SCHEMA IF NOT EXISTS {self.raw().layerName()}')
            self.executeSql(f'CREATE SCHEMA IF NOT EXISTS {self.clean().layerName()}')
            self.executeSql(f'CREATE SCHEMA IF NOT EXISTS {self.BI().layerName()}')

    def onSchemaUpdate(self, table_name: str, table_group: str|None = None):
        if table_group:
            self.schemaUpdateDump(table_group)



    ###########################################################################
    # META
    ###########################################################################

    def metaTableExists(self, layer_name: str) -> bool:
        return self.tableExists('_meta', layer_name)
    
    def metaCreateTable(self, layer_name: str) -> None:
        Log.info(f'Creating Data Warehouse "{layer_name}.{self.META_TABLE_NAME}" table.')
        with self.createTable(self.META_TABLE_NAME, layer_name) as table:
            table.col('id').id()
            table.col('key').string().notNull()
            table.col('value_str').string()
            table.col('value_int').integer()
            table.col('value_datetime').datetime()
            table.indexUnique(['key'])

    def metaDropTable(self, layer_name: str):
        self.dropTable(self.META_TABLE_NAME, layer_name)

    def metaInsertOrUpdate(self, 
        layer_name: str,
        key: str, 
        val_str: str|None = None, 
        val_int: int|None = None,
        val_datetime: datetime|None = None
    ) -> None:
        
        meta = MetaRecordType(
            key=key,
            val_str=val_str,
            val_int=val_int,
            val_datetime=val_datetime
        )
        meta_df = self.metaSelectAll(layer_name)
        key_exists = key in meta_df['key'].to_list()
        if key_exists:
            self.update(self.META_TABLE_NAME, meta, 'key', meta.key, table_group=layer_name)
        self.insert(self.META_TABLE_NAME, meta, table_group=layer_name)

    def metaSelectAll(self, layer_name: str) -> pl.DataFrame:
        table = self.table(self.META_TABLE_NAME, table_group=layer_name)
        df = pl.from_pandas(table.execute())
        return df
    
    def metaDelete(self, layer_name: str, key: str) -> None:
        self.delete(self.META_TABLE_NAME, 'key', key, table_group=layer_name)



    ###########################################################################
    # META LAST SYNC
    ###########################################################################

    def generateLastSyncKey(self, extractor: TabularDataExtractor, table_name: str) -> str:
        source_table = self.generateSourceTableName(extractor, table_name)
        key = 'last_sync__' + source_table
        return key

    def updateLastSyncDate(self, 
        layer_name: str, 
        extractor: TabularDataExtractor, 
        table_name: str
    ) -> None:
        '''
        Write current UTC datetime to the meta table
        Use for when a specific source:table was fetched last time
        '''
        key = self.generateLastSyncKey(extractor, table_name)
        time_now = datetime.now(timezone.utc)
        self.metaInsertOrUpdate(layer_name, key, val_datetime=time_now)

    def getLastSyncDate(self, 
        layer_name: str, 
        extractor: TabularDataExtractor, 
        table_name: str
    ) -> datetime|None:
        df = self.metaSelectAll(layer_name)
        key = self.generateLastSyncKey(extractor, table_name)
        key_exists = key in df['key'].to_list()
        if key_exists:
            return df.filter(pl.col('key') == key).get_column('val_datetime')[0]
        return None
    


    ###########################################################################
    # SCHEMA DUMP FOR LLM
    ###########################################################################

    def schemaFilePath(self, layer_name: str) -> str:
        if layer_name == self._rawLayerName:
            return self._schemaFilePathRaw
        elif layer_name == self._cleanLayerName:
            return self._schemaFilePathClean
        else:
            return self._schemaFilePathBI

        
    def schemaUpdateDump(self, layer_name: str) -> None:
        file_path = self.schemaFilePath(layer_name)
        sql = self.showCreateTablesAsDump(layer_name)
        with open(file_path, 'w') as f:
            f.write(sql)

    def schemaGetDump(self, layer_name: str) -> str|None:
        try:
            file_path = self.schemaFilePath(layer_name)
            with open(file_path, 'r') as f:
                return f.read()
        except (FileNotFoundError, ValueError):
            return None
        


    ###########################################################################
    # DATA SOURCES
    ###########################################################################
        
    def generateSourceTableName(self, extractor: TabularDataExtractor, table_name: str) -> str:
        return snake(extractor.NAME) + '__' + snake(table_name)


    
    ###########################################################################
    # RAW (BRONZE) LAYER
    ###########################################################################

    def raw(self) -> DataWarehouseLayerScope:
        return self._rawLayerScope
    
    ###########################################################################
    # CLEAN (SILVER) LAYER
    ###########################################################################

    def clean(self) -> DataWarehouseLayerScope:
        return self._cleanLayerScope

    ###########################################################################
    # BI (BUSINESS INTELLIGENCE, GOLD) LAYER
    ###########################################################################

    def BI(self) -> DataWarehouseLayerScope:
        return self._BILayerScope
    