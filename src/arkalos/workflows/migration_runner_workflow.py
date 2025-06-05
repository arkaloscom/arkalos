
import os
import importlib
from dataclasses import dataclass

import polars as pl

from arkalos.core.path import migration_path
from arkalos.core.logger import log as Log
from arkalos.workflows.workflow import Workflow
from arkalos.data.database.database import Database
from arkalos.schema.ddl.table_builder import TableBuilder



@dataclass
class MigrationType:
    version: str
    migration: str



class MigrationRunnerWorkflow(Workflow):

    MIGRATIONS_TABLE_NAME: str = '_migrations'

    _connection: Database

    def __init__(self, connection: Database):
        self._connection = connection

    def onBeforeRun(self):
        cls_name = self._connection.__class__.__name__
        engine = self._connection.getEngineName()
        db = self._connection.getDatabaseName()
        Log.info(f'Connection Class: {cls_name} | Engine: {engine} | Database: {db}')
        self._connection.connect()

    def onAfterRun(self):
        self._connection.disconnect()

    def migrationTableExists(self):
        return self._connection.tableExists(self.MIGRATIONS_TABLE_NAME)
    
    def createMigrationsTable(self):
        Log.info(f'First run. Creating "{self.MIGRATIONS_TABLE_NAME}" table.')
        with self._connection.createTable(self.MIGRATIONS_TABLE_NAME) as table:
            table.col('id').id()
            table.col('version').string().notNull()
            table.col('migration').string().notNull()
            table.col('created_at').datetime().notNull().defaultNow()
            table.indexUnique(['version', 'migration'])

    def dropMigrationsTable(self):
        self._connection.dropTable(self.MIGRATIONS_TABLE_NAME)

    def insertIntoMigrationsTable(self, version: str, module_name: str):
        migration = MigrationType(
            version=version,
            migration=module_name
        )
        self._connection.insert(self.MIGRATIONS_TABLE_NAME, migration)

    def selectMigrations(self) -> pl.DataFrame|None:
        table = self._connection.table(self.MIGRATIONS_TABLE_NAME)
        df = pl.from_pandas(table.execute())
        if df.is_empty():
            return None
        return df
    
    def deleteMigration(self, module_name):
        self._connection.delete(self.MIGRATIONS_TABLE_NAME, 'migration', module_name)

    def run(self, version: str|None = None, rollback: bool = False):
        
        if not self.migrationTableExists():
            self.createMigrationsTable()

        df = self.selectMigrations()

        count = 0
        if version is None:
            # Run all migrations (all versions)
            versions = self.getAllVersionFolders(reverse=rollback)
            versions = self.getAllVersionFoldersAfterLast(versions, df)
            for version in versions:
                count += self.importAndRunMigrationVersion(version, df, rollback)
        else:
            # Run specific version's migrations
            count += self.importAndRunMigrationVersion(version, df, rollback)

        if count == 0:
            Log.info('Nothing to migrate.')



    def formatVersionStr(self, version: str) -> str:
        version = version.replace('.', '_')
        if not version.startswith('v'):
            version = 'v' + version
        return version

    def getAllVersionFolders(self, reverse: bool = False) -> list[str]:
        warehouse = self._connection.isDataWarehouse()
        migrations_base_path = migration_path(version=None, warehouse=warehouse)
        version_folders = []

        for item in os.listdir(migrations_base_path):
            item_path = os.path.join(migrations_base_path, item)
            if os.path.isdir(item_path) and item.startswith('v'):
                version_folders.append(item)
        
        version_folders.sort(reverse=reverse)
        return version_folders
    
    def getAllVersionFoldersAfterLast(self, 
        versions: list[str], 
        df: pl.DataFrame|None
    ) -> list[str]:

        if df is None:
            return versions
        
        last_version = self.formatVersionStr(df.tail(1).get_column('version')[0])

        def parse_version(v):
            return tuple(map(int, v[1:].split('_')))

        last_version_parsed = parse_version(last_version)
        filtered = [v for v in versions if parse_version(v) >= last_version_parsed]
        return filtered

    
    def getMigrationsInVersion(self, version: str, reverse: bool = False) -> list[str]:
        warehouse = self._connection.isDataWarehouse()
        migrations_path = migration_path(version=version, warehouse=warehouse) 
        migration_files = sorted((f for f in os.listdir(migrations_path) if f.endswith('.py')), reverse=reverse)
        migrations = []

        for filename in migration_files:
            module_name = filename[:-3]
            migrations.append(module_name)

        return migrations

    def importAndRunMigrationVersion(self, version: str, df: pl.DataFrame|None, rollback: bool) -> int:
        version = self.formatVersionStr(version)
        folder = 'dwh' if self._connection.isDataWarehouse() else 'db'
        migration_module_names = self.getMigrationsInVersion(version, reverse=rollback)
        
        count = 0
        for module_name in migration_module_names:
            mig_exists_in_db = False
            if df is not None:
                mig_exists_in_db = module_name in df['migration'].to_list()

            if rollback:
                if mig_exists_in_db:
                    self.importRunMigration(folder, version, module_name, rollback)
                    count += 1
            else:
                if not mig_exists_in_db:
                    self.importRunMigration(folder, version, module_name, rollback)
                    count += 1

        return count
            


    def importRunMigration(self, folder: str, version: str, module_name: str, rollback: bool):
        rb_word = ' down ' if rollback else ' up '
        Log.info(f'Running{rb_word}migration: app/schema/migrations/{folder}/{version}/{module_name}.py')
        module_path = f'app.schema.migrations.{folder}.{version}.{module_name}'
        module = importlib.import_module(module_path)
        cls = getattr(module, 'Migration')

        cls().run(rollback=rollback)

        if rollback:
            self.deleteMigration(module_name)
        else:
            self.insertIntoMigrationsTable(version, module_name)
