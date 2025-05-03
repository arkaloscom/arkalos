from arkalos.ai import AIAgent
from arkalos.ai import SearchDWHAction
from arkalos.ai import TextToSQLAction
from arkalos import dwh

class DWHAgent(AIAgent):
    
    NAME = "DWHAgent"
    DESCRIPTION = "Talk to a data warehouse. Converts natural language to SQL and queries data."
    GREETING = "Hello! I am a DWHAgent and can help you query the data warehouse. What would you like to know?"
    ACTIONS = [
        TextToSQLAction,
        SearchDWHAction
    ]
    
    def setup(self) -> None:
        dwh().connect()
    
    def cleanup(self) -> None:
        dwh().disconnect()

    async def textToSQL(self, message: str) -> str:
        return await self.runAction(TextToSQLAction, message)
    
    async def searchDWH(self, sql_query: str) -> str:
        df = await self.runAction(SearchDWHAction, sql_query)
        return self.dfToMarkdown(df)
    
    async def processMessage(self, message: str) -> str:
        sql_section = "Transforming text to SQL..."
        sql_query = await self.textToSQL(message)
        
        query_section = f"Running SQL:\n ```sql\n{sql_query}\n```"
        results_heading = "Here is what I found:"
        results_table = await self.searchDWH(sql_query)
        
        return f"{sql_section}\n\n{query_section}\n\n{results_heading}\n\n{results_table}"
