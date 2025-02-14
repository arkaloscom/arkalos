import polars as pl

from arkalos.ai import ConsoleEnv
from arkalos.ai import AIAgent
from arkalos.ai import SearchDWHTask
from arkalos.ai import TextToSQLTask
from arkalos import dwh

class DWHAgent(AIAgent):

    _env: ConsoleEnv

    @property
    def NAME(self) -> str:
        return 'DWHAgent'
    
    @property
    def DESCRIPTION(self) -> str:
        return 'Talk to your data warehouse. Converts natural language to SQL and attempts to SELECT data and present it as a DataFrame'

    @property
    def GREETING(self) -> str:
        return 'Hello! I can help you query the data warehouse. What would you like to know?'


    def __init__(self):
        self._env = ConsoleEnv(self.NAME, self.GREETING, self.action)
        self._tasks = {
            'text_to_sql': TextToSQLTask(),
            'search_dwh': SearchDWHTask()
        }

    def beforeRun(self):
        dwh().connect()

    def afterRun(self):
        dwh().disconnect()



    def action(self, user_input: str):
        self.message('Transforming text to SQL...')
        sql_query = self.runTask('text_to_sql', user_input)

        self.message(f"Running SQL: {sql_query}")
        df = self.runTask('search_dwh', sql_query)

        self.message('Here is what I found:')
        with pl.Config(tbl_rows=20, tbl_cols=15):
            print(df)


