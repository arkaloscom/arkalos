
from datetime import datetime

import polars as pl

from abc import ABC, abstractmethod
from dataclasses import dataclass



@dataclass
class DataExtractorConfig: 
    pass



class DataExtractor(ABC):
    NAME: str
    DESCRIPTION: str



class UnstructuredDataExtractor(DataExtractor):
    pass



class TabularDataExtractor(DataExtractor):
    
    CONFIG: DataExtractorConfig
    TABLES: dict

    @abstractmethod
    def fetchSchema(self, table_name: str) -> pl.Schema:
        pass

    @abstractmethod
    def fetchAllData(self, table_name: str) -> list[dict]:
        pass

    @abstractmethod
    def transformRow(self, data: dict) -> dict:
        pass

    @abstractmethod
    def fetchUpdatedData(self, table_name: str, last_sync_date: datetime) -> list[dict]:
        pass

    @abstractmethod
    def fetchAllIDs(self, table_name: str, column_name: str) -> list:
        pass



    def transformData(self, data) -> list[dict]:
        return [self.transformRow(row) for row in data]
        
    def getTableIdByName(self, table_name: str) -> str|None:
        for table in self.TABLES:
            if table['name'] == table_name:
                return str(table['id'])
        return None
