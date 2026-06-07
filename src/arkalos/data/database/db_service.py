
from typing import Any, TypedDict
from abc import ABC, abstractmethod
from dataclasses import dataclass



@dataclass
class DBReadMessageType:
    columns: list[str]
    rows: list[tuple]
    row_count: int

@dataclass
class DBWriteMessageType:
    rows_affected: int
    last_insert_id: Any

@dataclass
class DBErrorMessageType:
    error: str



class DBService(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def executeRead(self, sql: str, params: list|None = None) -> DBReadMessageType:
        pass

    @abstractmethod
    def executeWrite(self, sql: str, params: list|None = None) -> DBWriteMessageType:
        pass

    @abstractmethod
    def commit(self):
        pass

    def close(self):
        self.disconnect()
