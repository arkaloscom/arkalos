from typing import Type, Any, TYPE_CHECKING
from abc import ABC, abstractmethod

from arkalos.ai import AIEnv
from arkalos.ai import AITask, WhichTask



class AIAgent(ABC):

    _env: AIEnv
    _tasks: dict[str, AITask]

    @property
    @abstractmethod
    def NAME(self) -> str:
        pass

    @property
    @abstractmethod
    def DESCRIPTION(self) -> str:
        pass

    @property
    def GREETING(self) -> str:
        return ''
    

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def action(self, user_input: str) -> Any:
        pass

    

    def beforeRun(self):
        pass

    def afterRun(self):
        pass

    def env(self) -> AIEnv:
        return self._env
    
    def message(self, message: str):
        self.env().agentMessage(message)

    def run(self) -> None:
        self.beforeRun()
        self.env().runLoop()
        self.afterRun()

    def task(self, task_name) -> AITask:
        return self._tasks[task_name]

    def runTask(self, task_name: str, message: str) -> Any:
        task = self.task(task_name)
        return task.run(message)
    
    def whichTask(self, user_input):
        return WhichTask(self._tasks).run(user_input)