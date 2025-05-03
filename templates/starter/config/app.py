from arkalos import env

config = {

    'name': env('APP_NAME', 'Arkalos App'),

    'env': env('APP_ENV', 'production'),
    
    'debug': env('APP_DEBUG', False),

    'workers': env('APP_WORKERS', 1),

}
