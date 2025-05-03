import polars as pl

from arkalos import dwh
from arkalos.ai import AIAction



class SearchDWHAction(AIAction):

    NAME = 'search_dwh'
    DESCRIPTION = 'Search an SQL data warehouse by running SELECT queries and returning a DataFrame.'
    
    def getDataFromDWH(self, sql: str) -> tuple:
        results = dwh().selectQuery(sql)
        return results
    
    def resultsToDf(self, results: tuple) -> pl.DataFrame:
        result_rows = results[0]
        result_description = results[1]
        column_names = [description[0] for description in result_description]  # Get column names
        df = pl.DataFrame(result_rows, schema=column_names, orient='row')
        return df

    async def run(self, sql: str) -> pl.DataFrame:
        results = self.getDataFromDWH(sql)
        df = self.resultsToDf(results)
        return df
