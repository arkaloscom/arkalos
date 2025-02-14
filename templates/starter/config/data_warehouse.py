from arkalos import env

config = {
    # Current engine
    'engine': env('DWH_ENGINE', 'sqlite'),
    'schema_path': env('DWH_SCHEMA_PATH', 'data/dwh/dwh.sql'),
    'sync_frequency': '1h',

    # SQLite
    'path': env('DWH_SQLITE_PATH', 'data/dwh.db'),

    # PostgreSQL, etc.
    'host': env('DWH_HOST', '127.0.0.1'),
    'port': env('DWH_PORT', '3306'),
    'database': env('DWH_DATABASE', 'warehouse'),
    'username': env('DWH_USERNAME', 'root'),
    'password': env('DWH_PASSWORD', ''),

    # Available engines
    'engines': {
        'sqlite': {},
        #'postgresql': {},
        #'bigquery': {},
        #'snowflake': {}
    }
}
