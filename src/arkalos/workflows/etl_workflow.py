
from arkalos.data.extractors.data_extractor import TabularDataExtractor
from arkalos.data.warehouse.data_warehouse import DataWarehouse
from arkalos.core.dwh import dwh

from arkalos.workflows.workflow import Workflow

class ETLWorkflow(Workflow):

    __extractor: TabularDataExtractor
    __dwh: DataWarehouse
    __tables: dict

    def __init__(
        self, 
        data_extractor_class: type[TabularDataExtractor], 
        data_warehouse_class: type[DataWarehouse]|None = None
    ):
        self.__extractor = data_extractor_class()
        self.__dwh = data_warehouse_class() if data_warehouse_class is not None else dwh()
        self.__tables = self.__extractor.TABLES

    def __1fetchData(self, table_name: str):
        print(f'1. Fetching data from source ({self.__extractor.NAME}) table "{table_name}"...')
        data = self.__extractor.fetchAllData(table_name)
        return data

    def __2detectSchema(self, data):
        print('2. Detecting schema...')
        data_schema = self.__dwh.detectDataSchema(data)
        return data_schema
    
    def __3createWhTable(self, table_name, data_schema, drop_table=False):
        print(f'3. Creating a new table in destination warehouse "{self.__dwh.generateTableName(self.__extractor, table_name)}"...')
        if (drop_table):
            print('- Dropping table...')
            self.__dwh.dropTable(self.__extractor, table_name)
        self.__dwh.createTable(self.__extractor, table_name, data_schema)

    def __4importDataIntoWh(self, table_name, data_schema, data):
        print('4. Importing data into a warehouse...')
        self.__dwh.importData(self.__extractor, table_name, data_schema, data)
        print()

    def __runSingleTable(self, table_name, drop_table=False):
        data = self.__1fetchData(table_name)
        data_schema = self.__2detectSchema(data)
        self.__3createWhTable(table_name, data_schema, drop_table)
        self.__4importDataIntoWh(table_name, data_schema, data)

    def __runStartMessage(self):
        print()
        print(f'Start Syncing Data Source ({self.__extractor.NAME}) with Data Warehouse ({self.__dwh.NAME})...')
        print()

    def __runEndMessage(self):
        print('DONE.')
        print()

    def __error(self, message):
        RED = '\033[31m'
        RESET = '\033[0m'  # Reset to default color
        print(f"{RED}ERROR: {message}{RESET}")

    def run(self, drop_tables=False):

        try:
            self.__runStartMessage()
            self.__dwh.connect()
            self.__dwh.updateLastSyncDate()

            for table in self.__tables:
                self.__runSingleTable(table['name'], drop_tables)

            self.__dwh.disconnect()
            self.__runEndMessage()
        except Exception as e:
            self.__error(e)
