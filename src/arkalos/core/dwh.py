
from arkalos.core.registry import Registry
from arkalos.data.warehouse.data_warehouse import DataWarehouse

Registry.register('dwh', DataWarehouse, True)

def DWH() -> DataWarehouse:
    return Registry.get('dwh')
