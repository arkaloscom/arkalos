
from arkalos.core.registry import Registry
from arkalos.data.database.database import Database

Registry.register('db', Database, True)

def DB() -> Database:
    return Registry.get('db')
