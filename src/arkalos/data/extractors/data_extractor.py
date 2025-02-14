from abc import ABC, abstractmethod

class DataExtractor(ABC):

    TYPE_CONNECTION = 1
    TYPE_HTTP_REQUEST = 2
    TYPE_OTHER = 3

    @property
    @abstractmethod
    def TYPE(self) -> int:
        pass

    @property
    @abstractmethod
    def NAME(self) -> str:
        pass

    @property
    @abstractmethod
    def CONFIG(self) -> dict:
        pass

    @property
    @abstractmethod
    def TABLES(self) -> dict:
        pass



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



    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def request(self, url_endpoint, params = None) -> None:
        pass

    def transformData(self, data):
        return [self.transformRow(row) for row in data]
        
    def getTableIdByName(self, table_name) -> str|None:
        for table in self.TABLES:
            if table['name'] == table_name:
                return str(table['id'])
        return None
