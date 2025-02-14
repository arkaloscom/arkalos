
from arkalos.core.registry import Registry
from arkalos.core.config import config
from arkalos.data.warehouse.data_warehouse import DataWarehouse
from arkalos.data.warehouse.sqlite.sqlite_warehouse import SQLiteWarehouse

engine = config('data_warehouse.engine', 'sqlite')
Registry.register('dwh', SQLiteWarehouse, True)

def dwh() -> DataWarehouse:
    return Registry.get('dwh')
