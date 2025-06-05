import os
import sys
import re
from pathlib import Path
from datetime import datetime, timezone
from arkalos.utils.str_utils import snake

from arkalos.core.path import arkalos_templates_path, base_path



class MakeMigrationCommand:

    _isWarehouse: bool
    _version: str|None
    _tableName: str|None
    _categoryFolder: str

    def __init__(self, warehouse: bool = False):
        self._isWarehouse = warehouse
        self._categoryFolder = 'dwh' if warehouse else 'db'
        parts = self.parseArgs()
        if parts:
            self._version = parts['version']
            self._tableName = parts['table_name']
        else:
            self._version = None
            self._tableName = None

    def printNoArgMessage(self):
        suffix = ':dwh' if self._isWarehouse else ''
        print('Please provide a migration table name.')
        print(f'Usage: uv run arkalos make:mig{suffix} <version>/<table_name>')

    def parseArgs(self):
        if len(sys.argv) < 3:
            return False
        
        arg = sys.argv[2]
        version = '0.0.0'
        table_name = 'table'

        if '/' in arg:
            version, table_name = arg.split('/', 1)
        else:
            version = '0.0.0'
            table_name = arg

        version = version.replace('.', '_')

        return {
            'table_name': snake(table_name),
            'version': version
        }

    def run(self):
        if self._tableName is None:
            self.printNoArgMessage()
            return

        timestamp_utc = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        
        file_name = f'v{timestamp_utc}_create_{self._tableName}_table.py'
        
        template_file = 'migration_dwh.py' if self._isWarehouse else 'migration.py'
        template_file = Path(arkalos_templates_path()) / 'make' / template_file
        destination_dir = Path(base_path(f'app/schema/migrations/{self._categoryFolder}/v{self._version}'))
        destination_file = destination_dir / file_name
        
        os.makedirs(destination_dir, exist_ok=True)
        if destination_file.exists():
            print(f"Error: File '{file_name}' already exists.")
            return
        
        with open(template_file, 'r') as f:
            template_content = f.read()
        
        # Replace placeholder
        new_content = template_content.replace('MAKE', self._tableName)
        
        with open(destination_file, 'w') as f:
            f.write(new_content)
        
        print(f'Migration created successfully: {destination_file}')
