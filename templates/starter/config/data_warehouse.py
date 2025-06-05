
from arkalos import env

config = {
    
    # Current engine
    'engine': env('DWH_ENGINE', 'sqlite'),

    # Meta
    'schema_path_raw': 'data/dwh/schema_raw.sql',
    'schema_path_clean': 'data/dwh/schema_clean.sql',
    'schema_path_bi': 'data/dwh/schema_bi.sql',

    # Available layers and their names, table groups (aka collections, schemas, etc)
    'layer_raw': 'raw',
    'layer_clean': 'clean',
    'layer_bi': 'bi',

    # SQLite
    'path': 'data/dwh/dwh.db',
    'path_raw': 'data/dwh/dwh_raw.db',
    'path_clean': 'data/dwh/dwh_clean.db',
    'path_bi': 'data/dwh/dwh_bi.db',

    # DuckDB
    'path_ddb': 'data/dwh/dwh.ddb',

    # PostgreSQL, etc.
    'host': env('DWH_HOST', '127.0.0.1'),
    'port': env('DWH_PORT', '3306'),
    'database': env('DWH_DATABASE', 'warehouse'),
    'username': env('DWH_USERNAME', 'root'),
    'password': env('DWH_PASSWORD', ''),

}
