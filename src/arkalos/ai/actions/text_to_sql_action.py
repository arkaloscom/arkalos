import re

from arkalos import DWH, config
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
        warehouse_schema = DWH().schemaGetDump(DWH().raw().layerName())
        prompt = f"""
            ### Instructions:
            Your task is to convert a question into a SQL query, given {DWH().getEngineName()} database schema.
            
            Go through the question and database schema word by word.

            There are 3 layers (databases). Each table name always must be prefixed with one of them:
            - raw
            - clean
            - bi

            Use this DB dialect and engine: {DWH().getEngineName()}

            For sqlite only, that shall include all the built-in and any other tables like 'sqlite_master'.
            For sqlite only, to list all the tables, use the raw layer, i.e. law.sqlite_master.
            For sqlite only, sqlite only has NULL, INTEGER, REAL, TEXT, BLOB types. It doesn't have many functions.
            For duckdb, use main.duckdb_tables

            ### Input:
            Generate a SQL query only without any comments, and that answers the question:
            
            `{message}`.

            This query will run on a database whose schema is represented in this string:

            {warehouse_schema}
                    
            ### Response:
            ```sql
        """

        ai_conf_name = config('ai.use_actions')['text2sql']
        response = await self.generateTextResponse(prompt, ai_conf_name)
        sql_query = self.extractSQLFromMessage(response)
        return sql_query
    