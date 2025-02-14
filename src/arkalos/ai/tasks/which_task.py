
from arkalos.ai import AITask



class WhichTask(AITask):

    _tasks: dict[str, AITask]

    @property
    def NAME(self):
        return 'which_task'
    
    @property
    def DESCRIPTION(self):
        return 'Understand the intent and which task from the available list fits the prompt'


    def __init__(self, tasks: dict[str, AITask]):
        self._tasks = tasks


    def buildTaskListForPrompt(self):
        task_list = ''
        for task_key in self._tasks:
            task_list = task_list + task_key + ': ' + self._tasks[task_key].DESCRIPTION + '\n'
        return task_list

    def run(self, message) -> str:
        task_list = self.buildTaskListForPrompt()
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

        response = self.generateTextResponse(prompt)
        return response
    