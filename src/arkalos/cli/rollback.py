
import sys

from arkalos.core.db import DB
from arkalos.workflows.migration_runner_workflow import MigrationRunnerWorkflow

def run() -> None:
    version: str|None = None
    connection = DB()
    if len(sys.argv) >= 3:
        version = sys.argv[2]
    
    wf = MigrationRunnerWorkflow(connection)
    wf.execute(version=version, rollback=True)
