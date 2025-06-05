
from arkalos import env

config = {

    # Current engine
    'engine': env('DB_ENGINE', 'sqlite'),

    # SQLite
    'path': 'data/db/db.db',

    # PostgreSQL, etc.
    'host': env('DB_HOST', '127.0.0.1'),
    'port': env('DB_PORT', '3306'),
    'database': env('DB_DATABASE', 'app'),
    'username': env('DB_USERNAME', 'root'),
    'password': env('DB_PASSWORD', ''),

}
