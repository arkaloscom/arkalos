from typing import Callable, TYPE_CHECKING

from arkalos.ai import AIEnv

class ConsoleEnv(AIEnv):

    __agent_name: str
    __greeting: str
    __action: Callable

    def __init__(self, agent_name: str, greeting: str, action_fn: Callable):
        self.__agent_name = agent_name
        self.__greeting = greeting
        self.__action = action_fn

    def agentMessage(self, message: str):
        print(f"{self.__agent_name}: {message}")

    def runLoop(self):
        try:
            self.agentMessage(self.__greeting)

            while True:
                user_input = input("You: ")

                if user_input.lower() in ["exit", "quit", "bye"]:
                    self.agentMessage('Goodbye!')
                    break

                try:
                    self.__action(user_input)
                    print()
                    self.agentMessage('Anything else I can help you with?')

                except Exception as e:
                    self.agentMessage(f"Oops! Something went wrong: {e}")
            
        except (EOFError, KeyboardInterrupt):
            print()
            self.agentMessage('Goodbye!')
