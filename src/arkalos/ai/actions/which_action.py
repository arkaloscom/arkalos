
from arkalos.ai import AIAction



class WhichAction(AIAction):

    _actions: dict[str, AIAction]

    NAME = 'which_action'
    DESCRIPTION = 'Understand the intent and which action (task) from the available list fits the prompt'



    def __init__(self, actions: dict[str, AIAction]):
        self._actions = actions



    def buildActionListForPrompt(self):
        task_list = ''
        for task_key in self._actions:
            task_list = task_list + task_key + ': ' + self._actions[task_key].DESCRIPTION + '\n'
        return task_list

    async def run(self, message) -> str:
        task_list = self.buildActionListForPrompt()
        prompt = f"""
            ### Instructions:
            Your task is to understand the intent of the input and provide a task name.
            
            Go through the question and task list word by word.

            ### Input:
            Determine which task could answer the question `{message}`.

            Task list is represented in this string and in this format (task name: task description):

            {task_list}
                    
            ### Response:
            Respond with a string only, a key name from the list (before the ":")
        """

        response = await self.generateTextResponse(prompt)
        return response
    