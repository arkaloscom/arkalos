import polars as pl

from arkalos import dwh
from arkalos.ai import AITask



class SearchDWHTask(AITask):

    @property
    def NAME(self):
        return 'search_dwh'
    
    @property
    def DESCRIPTION(self):
        return 'Search an SQL data warehouse by running SELECT queries and returning a DataFrame.'
    
    def getDataFromDWH(self, sql: str) -> tuple:
        results = dwh().selectQuery(sql)
        return results
    
    def resultsToDf(self, results: tuple) -> pl.DataFrame:
        result_rows = results[0]
        result_description = results[1]
        column_names = [description[0] for description in result_description]  # Get column names
        df = pl.DataFrame(result_rows, schema=column_names, orient='row')
        return df

    def run(self, sql: str) -> pl.DataFrame:
        results = self.getDataFromDWH(sql)
        df = self.resultsToDf(results)
        return df
