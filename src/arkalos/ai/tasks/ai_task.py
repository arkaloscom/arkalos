import ollama

from typing import Any, Optional
from abc import ABC, abstractmethod

from arkalos import config

class AITask(ABC):

    @property
    @abstractmethod
    def NAME(self) -> str:
        pass

    @property
    @abstractmethod
    def DESCRIPTION(self) -> str:
        pass
    
    @abstractmethod
    def run(self, message: str) -> Any:
        pass

    def generateTextResponse(self, prompt: str, model: Optional[str] = None):
        if (model is None):
            model = config('app.llm')
        response = ollama.generate(model=model, prompt=prompt)
        return response["response"].strip()