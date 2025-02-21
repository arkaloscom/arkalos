from typing import Any
from abc import ABC, abstractmethod

import ollama

from arkalos import config



class AIAction(ABC):

    NAME: str
    DESCRIPTION: str
    
    @abstractmethod
    def run(self, message: str) -> Any:
        pass

    def generateTextResponse(self, prompt: str, model: str|None = None):
        if (model is None):
            model = config('app.llm')
        response = ollama.generate(model=model, prompt=prompt)
        return response["response"].strip()
