
import os
from pathlib import Path
from functools import lru_cache

_PROJECT_ROOT: str|None = None

@lru_cache()
def _get_project_root() -> str:
    '''Get the project root path, caching the result'''
    global _PROJECT_ROOT
    
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT
        
    # Start from the current working directory
    current = Path.cwd()
    while current != current.parent:
        # Look for markers that indicate project root
        if any((current / marker).exists() for marker in ['pyproject.toml', '.env', '.git']):
            _PROJECT_ROOT = str(current)
            return _PROJECT_ROOT
        current = current.parent
        
    raise RuntimeError('Could not find project root')

def _norm_path(path: str|None = None) -> str:
    if path is None:
        path = ''
    return path.replace('/', os.sep).replace('\\', os.sep).lstrip(os.sep)

def base_path(path: str|None = None) -> str:
    '''Get a path relative to the project root.'''
    path = _norm_path(path)
    if path:
        return _get_project_root() + os.sep + path
    return _get_project_root()

def drive_path(path: str|None = None) -> str:
    '''Get a path relative to the 'data/drive' directory within the project root.'''
    path = _norm_path(path)
    dir = 'data' + os.sep + 'drive'
    if path:
        dir = dir + os.sep + path
    return base_path(dir)

def arkalos_path(path: str|None = None) -> str:
    '''Get a path relative to installed arkalos package root inside site-packages.'''
    if path is None:
        path = ''
    return str(Path(__file__).parent.parent.joinpath(path))
