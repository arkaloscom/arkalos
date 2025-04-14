
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
    def fetchSchema(self) -> None:
        pass

    @abstractmethod
    def fetchAllData(self, table_name) -> None:
        pass

    @abstractmethod
    def transformRow(self, data) -> None:
        pass

    @abstractmethod
    def fetchUpdatedData(self, table_name, last_sync_date) -> None:
        pass

    @abstractmethod
    def fetchAllIDs(self, table_name, column_name = None) -> None:
        pass



    def transformData(self, data):
        return [self.transformRow(row) for row in data]
        
    def getTableIdByName(self, table_name) -> str|None:
        for table in self.TABLES:
            if table['name'] == table_name:
                return str(table['id'])
        return None
