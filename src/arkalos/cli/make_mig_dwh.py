
from arkalos.cli.common.make_migration_command import MakeMigrationCommand



def run():
    MakeMigrationCommand(warehouse=True).run()
    