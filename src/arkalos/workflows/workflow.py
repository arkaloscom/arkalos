from abc import ABC, abstractmethod
from arkalos.core.logger import log as Log
import time
import inspect
import os

class Workflow(ABC):

    def onBeforeRun(self):
        pass

    def onAfterRun(self):
        pass
    
    @abstractmethod
    def run(self):
        pass

    def execute(self, *args, **kwargs):
        try:
            filename = os.path.basename(inspect.getfile(self.__class__))
            Log.info('Running Workflow ' + self.__class__.__name__ + ' from ' + filename)
            start_time = time.time()
            self.onBeforeRun()
            self.run(*args, **kwargs)
            self.onAfterRun()
            end_time = time.time()
            duration = end_time - start_time
            Log.info(f'Done. Total time: {duration:.2f}s')
        except Exception as e:
            Log.exception(e)
