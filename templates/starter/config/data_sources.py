from arkalos import env

config = {
    'airtable': {
        'enabled': False,
        'api_key': env('AIRTABLE_API_KEY'),
        'base_id': env('AIRTABLE_BASE_ID'),
        'tables': env('AIRTABLE_TABLES'),
    },

    'google': {
        'enabled': False,
        'oauth_key_path': env('GOOGLE_OAUTH_KEY_PATH'),
        'service_account_key_path': env('GOOGLE_SERVICE_ACCOUNT_KEY_PATH'),
        'spreadsheets': env('GOOGLE_SPREADSHEETS'),
        'id_col': 'id',
        'updated_at_col': 'updated_at'
    },

    'hubspot': {
        'enabled': False,
        'api_key': env('HUBSPOT_API_KEY'),
        'objects': ['contacts', 'companies', 'deals'],
    },

    'monday': {
        'enabled': False,
        'api_key': env('MONDAY_API_KEY'),
        'databases': env('MONDAY_DATABASES'),
    },
    
    'notion': {
        'enabled': False,
        'api_secret': env('NOTION_API_SECRET'),
        'databases': env('NOTION_DATABASES'),
    },
    

}
