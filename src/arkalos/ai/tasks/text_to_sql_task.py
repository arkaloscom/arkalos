import re

from arkalos import dwh
from arkalos.ai import AITask



class TextToSQLTask(AITask):

    @property
    def NAME(self):
        return 'text_to_sql'
    
    @property
    def DESCRIPTION(self):
        return 'Transforms a natural language input into an SQL statement based on a data warehouse schema.'

    def extractSQLFromMessage(self, message: str) -> str:
        pattern = r'```(?:sql)?\s*(.*?)\s*```'
        match = re.search(pattern, message, re.DOTALL)
        if match:
            return match.group(1).strip()
        raise Exception('TextToSQLTask.extractSQLFromMessage: SQL not found in the message.')

    def run(self, message) -> str:
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

        response = self.generateTextResponse(prompt)
        sql_query = self.extractSQLFromMessage(response)
        return sql_query
    