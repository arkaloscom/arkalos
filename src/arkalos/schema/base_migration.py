
from typing import Callable
from abc import ABC, abstractmethod



class BaseMigration(ABC):

    @abstractmethod
    def up(self):
        pass

    @abstractmethod
    def down(self):
        pass

    def run(self, rollback: bool = False):
        if rollback:
            self.down()
        else:
            self.up()
