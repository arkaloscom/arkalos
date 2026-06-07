
import os
from pathlib import Path
import importlib
from typing import Type


from arkalos.core.path import base_path
from arkalos.workflows.workflow import Workflow
from arkalos.core.logger import log as Log



class WorkflowService:

    _path: str

    def __init__(self, workflows_path: str|None = None):
        self._path = workflows_path if workflows_path else base_path('app/workflows')

    def listWorkflows(self) -> list:
        wf_path = Path(self._path)
        workflow_paths = []
        
        # Find all *_workflow.py files recursively
        for workflow_file in wf_path.rglob("*_workflow.py"):
            rel_path = workflow_file.relative_to(wf_path)
            # Remove "_workflow.py" suffix and get the short path
            folder_part = str(rel_path.parent) if rel_path.parent != Path(".") else ""
            name_part = workflow_file.stem[:-9]
            
            if folder_part:
                workflow_paths.append(f"{folder_part}/{name_part}")
            else:
                workflow_paths.append(name_part)
        
        return workflow_paths

    def importRunWorkflow(self, short_path: str) -> bool:
        try:
            short_path = short_path.replace('/', '.')
            module_path = f'app.workflows.{short_path}_workflow'
            module = importlib.import_module(module_path)
            
            # Find class ending with "Workflow"
            workflow_class: Type[Workflow]|None = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type)
                    and name.endswith('Workflow') 
                    and obj.__module__ == module.__name__  # Defined in this module, not imported parent
                ):
                    workflow_class = obj
                    break
            
            if workflow_class:
                workflow_class().execute()
            else:
                raise ValueError(f"No class ending with 'Workflow' found in {module_path}")
            return True
        except ModuleNotFoundError:
            return False
