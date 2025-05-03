import re

from arkalos import dwh, config
from arkalos.ai import AIAction



class TextToSQLAction(AIAction):

    NAME = 'text_to_sql'
    DESCRIPTION = 'Transforms a natural language input into an SQL statement based on a data warehouse schema.'

    def extractSQLFromMessage(self, message: str) -> str:
        pattern = r'```(?:sql)?\s*(.*?)\s*```'
        match = re.search(pattern, message, re.DOTALL)
        if match:
            return match.group(1).strip()
        raise Exception('TextToSQLTask.extractSQLFromMessage: SQL not found in the message.')

    async def run(self, message) -> str:
        warehouse_schema = dwh().getSchemaDefinitions()
        prompt = f"""
            ### Instructions:
            Your task is to convert a question into a SQL query, given SQLite database schema.
            
            Go through the question and database schema word by word.

            ### Input:
            Generate a SQL query that answers the question `{message}`.

            This query will run on a database whose schema is represented in this string:

            {warehouse_schema}
                    
            ### Response:
            ```sql
        """

        ai_conf_name = config('ai.use_actions')['text2sql']
        response = await self.generateTextResponse(prompt, ai_conf_name)
        sql_query = self.extractSQLFromMessage(response)
        return sql_query
    