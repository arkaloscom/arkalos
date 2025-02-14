
from typing import Type, TYPE_CHECKING
from abc import ABC, abstractmethod


class AIEnv(ABC):

    @abstractmethod
    def agentMessage(self, message: str):
        pass
    
    @abstractmethod
    def runLoop(self):
        pass
