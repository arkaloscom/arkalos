
from dataclasses import dataclass
import requests

from arkalos import config
from arkalos.data.extractors.data_extractor import TabularDataExtractor, DataExtractorConfig



@dataclass
class NotionConfig(DataExtractorConfig):
    API_SECRET: str



class NotionExtractor(TabularDataExtractor):

    NAME = 'Notion'
    DESCRIPTION = 'Notion data extractor for Notion databases only'
    CONFIG: NotionConfig

    def __init__(self):
        self.CONFIG = NotionConfig(API_SECRET=config('data_sources.notion.api_secret'))
        self.TABLES = config('data_sources.notion.databases')



    def requestPages(self, url_endpoint):
        num_pages = None
        get_all = num_pages is None
        page_size = 100 if get_all else num_pages

        data = self.request(url_endpoint)

        results = data["results"]
        while data["has_more"] and get_all:
            payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
            data = self.request(url_endpoint=url_endpoint, params=payload)
            results.extend(data["results"])
        return results

    def request(self, url_endpoint, params = None):
        url = f'https://api.notion.com/v1/databases{url_endpoint}'
        headers = {
            'Authorization': f'Bearer {self.CONFIG.API_SECRET}',
            # 'Content-Type:': 'application/json',
            'Notion-Version': '2022-02-22'
        }

        response = requests.post(url=url, json=params, headers=headers)

        if response.status_code != 200:
            error_message = 'Error'
            if (response['object'] == 'error'):
                error_message = response['message']
            raise Exception(f"NotionExtractor.request: API request failed\nURL: {url}\nParams: {params}\nStatus: {response.status_code}\nMessage: {error_message}")
        return response.json()



    # TODO
    def fetchSchema(self, table_name):
        pass
    

    def fetchAllData(self, table_name):
        table_id = self.getTableIdByName(table_name)
        data = self.requestPages(f'/{table_id}/query')
        return self.transformData(data)
    
    def transformRow(self, data):
        # Notion returns data where each row is {
        #   archived, cover, created_by, created_time, icon, id, in_trash, last_edited_by, last_edited_time,
        #   object, parent, properties, public_url, url
        # }
        #
        # Properties contain column data of different types
        # Key is the title of the column
        # Value is an object {id, type, other keys depending on the type}. 
        # Column value is inside the key of the same name as type
        # e.g. Description column of the type rich_text will be 'Description': {id, type, rich_text, ...}
        #
        # Flatten object as {__id, **properties with only key: val}

        row = {'__id': data['id']}

        for key in data['properties']:
            col = data['properties'][key]
            type = col['type']
            method_name = '_extract_col_val_' + type
            if (hasattr(__class__, method_name)):
                method = getattr(__class__, method_name)
                row[key] = method(col)
            else:
                raise ValueError(f"Unsupported Notion type: {type}")

        return row
    
    def _extract_col_val_people(col_obj):
        # [{id, object}, ...]
        people_list = col_obj['people']
        people_ids = []
        for person in people_list:
            people_ids.append(person['id'])
        return people_ids

    def _extract_col_val_date(col_obj):
        # {start, end, time_zone}
        return col_obj['date']['start']
    
    def _extract_col_val_relation(col_obj):
        # [{id}]
        rel_list = col_obj['relation']
        rel_ids = []
        for rel in rel_list:
            rel_ids.append(rel['id'])
        return rel_ids
    
    def _extract_col_val_rollup(col_obj):
        # {function, number, type}
        return col_obj['rollup']['number']
    
    def _extract_col_val_select(col_obj):
        # {color, id, name}
        return col_obj['select']['id']
    
    def _extract_col_val_status(col_obj):
        # {color, id, name}
        return col_obj['status']['id']
    
    def _extract_col_val_rich_text(col_obj):
        # [{annotations: {}, href, plain_text, text: {content, link}, type}]
        return col_obj['rich_text'][0]['plain_text']
    
    def _extract_col_val_title(col_obj):
        # [{annotations: {}, href, plain_text, text: {content, link}, type}]
        return col_obj['title'][0]['plain_text']
    
    def _extract_col_val_multi_select(col_obj):
        # [{color, id, name}, ...]
        tag_list = col_obj['multi_select']
        tag_ids = []
        for tag in tag_list:
            tag_ids.append(tag['id'])
        return tag_ids

    def _extract_col_val_unique_id(col_obj):
        # {number, prefix}
        if (col_obj['unique_id']['prefix']):
            return col_obj['unique_id']['prefix'] + '-' + str(col_obj['unique_id']['number'])
        return col_obj['unique_id']['number']
    


    
    def fetchUpdatedData(self, table_name, last_sync_date):
        # table = self.__connection.table(self.CONFIG.BASE_ID, table_name)  
        # filter_formula = f"DATETIME_DIFF(LAST_MODIFIED_TIME(), '{last_sync_date}') > 0"
        # data = table.all(formula=filter_formula)
        # return self.transformData(data)
    
        results = self._request(table_name)
        return self.transformData(results)
    
    def fetchAllIDs(self, table_name):
        # table = self.__connection.table(self.CONFIG.BASE_ID, table_name)  
        # data = table.all(fields={})
        # return self.transformData(data)

        results = self._request(table_name)
        return self.transformData(results)