
import polars as pl

from arkalos.core.dwh import DWH
from arkalos.core.logger import log as Log
from arkalos.utils.schema import get_data_schema
from arkalos.data.extractors.data_extractor import TabularDataExtractor
from arkalos.data.warehouse.data_warehouse import DataWarehouse
from arkalos.workflows.workflow import Workflow



class ETLWorkflow(Workflow):

    _extractor: TabularDataExtractor
    _dwh: DataWarehouse
    _tables: dict

    def __init__(
        self, 
        extractor: type[TabularDataExtractor], 
        warehouse: type[DataWarehouse]|None = None
    ):
        self._extractor = extractor()
        self._dwh = warehouse() if warehouse is not None else DWH()
        self._tables = self._extractor.TABLES

    def _1fetchData(self, table_name: str) -> list[dict]:
        Log.info(f'1. Fetching data from source ({self._extractor.NAME}) table "{table_name}"...')
        data = self._extractor.fetchAllData(table_name)
        return data

    def _2detectSchema(self, data: list[dict]) -> pl.Schema:
        Log.info('2. Detecting schema...')
        data_schema = get_data_schema(data)
        return data_schema
    
    def _3createWhTable(self, table_name: str, data_schema: pl.Schema, drop_table: bool = False):
        norm_table_name = self._dwh.generateSourceTableName(self._extractor, table_name)
        Log.info(f'3. Creating a new table in the destination warehouse "{norm_table_name}"...')
        if (drop_table):
            Log.info('- Dropping table...')
            self._dwh.raw().dropTable(norm_table_name)
        self._dwh.raw().autoCreateTable(norm_table_name, data_schema)

    def _4importDataIntoWh(self, table_name: str, data: list[dict]):
        norm_table_name = self._dwh.generateSourceTableName(self._extractor, table_name)
        Log.info('4. Importing data into a warehouse...')
        self._dwh.raw().insertMultiple(norm_table_name, data)
        print()

    def _runSingleTable(self, table_name: str, drop_table: bool = False):
        data = self._1fetchData(table_name)
        data_schema = self._2detectSchema(data)
        self._3createWhTable(table_name, data_schema, drop_table)
        self._4importDataIntoWh(table_name, data)


    def onBeforeRun(self):
        cls_name = self._dwh.__class__.__name__
        engine = self._dwh.getEngineName()
        db = self._dwh.getDatabaseName()
        Log.info(f'Connection Class: {cls_name} | Engine: {engine} | Database: {db}')
        self._dwh.connect()

    def onAfterRun(self):
        self._dwh.disconnect()

    def run(self, drop_tables=False):
        Log.info(f'Start Syncing Data Source ({self._extractor.NAME}) into the Data Warehouse...')
        print()
        for table in self._tables:
            self._runSingleTable(table['name'], drop_tables)

