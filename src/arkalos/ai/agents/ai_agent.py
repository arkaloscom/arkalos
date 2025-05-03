import inspect
from typing import Type, Any, Dict, Callable
from abc import ABC, abstractmethod

import pandas as pd
import polars as pl

from arkalos.ai import AIAction, WhichAction
from arkalos.core.logger import log as Log



class AIAgent(ABC):
    """Base agent interface with direct runtime methods"""

    _actions: Dict[str, AIAction]
    
    NAME = "Agent"
    DESCRIPTION = "Agent has no description"
    GREETING = "Hi, I'm Agent. How can I help you?"
    ACTIONS: list[Type[AIAction]]
    


    # Init

    def __init__(self):
        self._actions = {}
        for action in self.ACTIONS:
            self._actions[action.NAME] = action()

    def setup(self) -> None:
        """Setup actions before processing messages"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup actions after processing messages"""
        pass


    # Interface methods

    @abstractmethod
    async def processMessage(self, message: str) -> str:
        """Process an incoming message and produce a response"""
        pass



    # Action methods
    
    def registerAction(self, action_id: str, task: AIAction) -> None:
        """Register a task with this agent"""
        self._actions[action_id] = task

    def registerActions(self, actions: Dict[str, AIAction]) -> None:
        """Register multiple tasks with this agent"""
        self._actions = actions
    
    async def runAction(self, action_or_id: str|Type[AIAction], message: str) -> Any:
        """Run a specific task"""
        action_id: str
        if inspect.isclass(action_or_id):
            action_id = action_or_id.NAME
        else:
            action_id = str(action_or_id)
        if action_id not in self._actions:
            raise KeyError(f"Action '{action_id}' not found")
        return await self._actions[action_id].run(message)
    
    async def whichAction(self, message: str):
        return await WhichAction(self._actions).run(message)
    

    
    # Direct runtime methods
    
    async def runConsole(self) -> None:
        """Run the agent in console mode"""
        self.setup()
        
        try:
            print(f"{self.NAME}: {self.GREETING}")
            
            while True:
                user_input = input("You: ")
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print(f"{self.NAME}: Goodbye!")
                    break
                
                try:
                    response = await self.processMessage(user_input)
                    print(f"{self.NAME}: {response}")
                    print()
                    print(f"{self.NAME}: Anything else I can help you with?")
                
                except Exception as e:
                    print(f"{self.NAME}: Oops! Something went wrong: {e}")
        
        except (EOFError, KeyboardInterrupt):
            print()
            print(f"{self.NAME}: Goodbye!")
            
        self.cleanup()
    
    async def handleHttp(self, message: str) -> dict[str, str]:
        """Handle an HTTP request and return JSON response"""
        self.setup()
        response = await self.processMessage(message)
        self.cleanup()
        return {"response": response}
    
    async def handleWebSocket(self, message: str, send_fn: Callable[[str], None]) -> None:
        """Handle a WebSocket message and send response"""
        try:
            self.setup()
            response = await self.processMessage(message)
            send_fn(response)
            self.cleanup()
        except Exception as e:
            Log.exception(e)
            send_fn(f"Error: {str(e)}")
    


    # Helpers

    def dfToMarkdown(self, df: pl.DataFrame|pd.DataFrame) -> str:
        """Format a DataFrame as markdown"""
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()
        return df.to_markdown(index=False)
