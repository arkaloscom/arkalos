
from pathlib import Path

import duckdb
from ibis.backends.duckdb import Backend # type: ignore

from arkalos.data.database.duckdb_service import DuckDBService
from arkalos.data.database.db_clerver import DBClerver

class ArkalosDuckDBBackend(Backend):

    def do_connect(self, database = ":memory:", read_only = False, extensions = None, **config):
        if not isinstance(database, Path) and not database.startswith(
            ("md:", "motherduck:", ":memory:")
        ):
            database = Path(database).absolute()

        service = DuckDBService(str(database))
        client = DBClerver(service)
        client.connect()
        self.con = client
        #self.con = duckdb.connect(str(database), config=config, read_only=read_only)
        self._post_connect(extensions)
