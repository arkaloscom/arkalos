
from dataclasses import dataclass
import requests

from arkalos import config
from arkalos.data.extractors.data_extractor import TabularDataExtractor, DataExtractorConfig



@dataclass
class AirtableConfig(DataExtractorConfig):
    API_KEY: str
    BASE_ID: str

class AirtableExtractor(TabularDataExtractor):

    NAME = 'Airtable'
    DESCRIPTION = 'Airtable data extractor for Airtable tables'
    CONFIG: AirtableConfig

    def __init__(self):
        self.CONFIG = AirtableConfig(
            API_KEY = config('data_sources.airtable.api_key'),
            BASE_ID = config('data_sources.airtable.base_id')
        )
        self.TABLES = config('data_sources.airtable.tables')



    def extractErrorMessage(self, response_json):
        if not isinstance(response_json, dict):
            return "Unknown error occurred"

        if isinstance(response_json.get("error"), dict):
            return response_json["error"].get("message", "Unknown error occurred")

        return response_json.get("error") or response_json.get("message") or "Unknown error occurred"


    def request(self, url_endpoint, params = None):
        url = f'https://api.airtable.com/v0{url_endpoint}'
        headers = {
            'Authorization': f'Bearer {self.CONFIG.API_KEY}',
            #'Content-Type:': 'application/json',
        }
        response = requests.get(url=url, params=params, headers=headers)
        if response.status_code != 200:
            error_message = self.extractErrorMessage(response.json())
            raise Exception(f"AirtableExtractor.request: API request failed\nURL: {url}\nParams: {params}\nStatus: {response.status_code}\nMessage: {error_message}")
        return response.json()
    
    def fetchSchema(self, table_name):
        data = self.request(f'/meta/bases/{self.CONFIG.BASE_ID}/tables')
        table_id = self.getTableIdByName(table_name)
        for table in data['tables']:
            if table['id'] == table_id:
                return table['fields'] # already has id and name keys
        raise KeyError(f"AirtableExtractor.fetchSchema: Table with ID '{table_id}' does not exist")

    def fetchAllData(self, table_name):
        table_id = self.getTableIdByName(table_name)
        data = self.request(f'/{self.CONFIG.BASE_ID}/{table_id}')
        data = data['records']
        return self.transformData(data)
    
    def transformRow(self, data):
        # Airtable returns data where each row is {id: str, createdTime: Datetime, fields: {}}
        # Flatten object as {__id, **fields}
        return {'__id': data['id'], **data['fields']}

    
    def fetchUpdatedData(self, table_name, last_sync_date):
        table_id = self.getTableIdByName(table_name)
        data = self.request(f'/{self.CONFIG.BASE_ID}/{table_id}', {
            'filterByFormula': f"DATETIME_DIFF(LAST_MODIFIED_TIME(), '{last_sync_date}') > 0"
        })
        data = data['records']
        return self.transformData(data)
    
    def fetchAllIDs(self, table_name, column_name):
        table_id = self.getTableIdByName(table_name)
        data = self.request(f'/{self.CONFIG.BASE_ID}/{table_id}', {
            'fields[]': column_name
        })
        data = data['records']
        ids = []
        for row in data:
            ids.append(row['id'])
        return ids