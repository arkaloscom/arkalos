from abc import ABC, abstractmethod

class Workflow(ABC):
    
    @abstractmethod
    def run(self):
        pass
