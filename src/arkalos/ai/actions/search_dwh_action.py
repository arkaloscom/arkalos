import polars as pl

from arkalos import DWH
from arkalos.ai import AIAction



class SearchDWHAction(AIAction):

    NAME = 'search_dwh'
    DESCRIPTION = 'Search an SQL data warehouse by running SELECT queries and returning a DataFrame.'

    async def run(self, sql: str) -> pl.DataFrame:
        return DWH().executeSql(sql, select=True)
