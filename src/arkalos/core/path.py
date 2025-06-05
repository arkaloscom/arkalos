
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

def migration_path(version: str|None = None, warehouse: bool = False):
    folder = 'dwh' if warehouse else 'db' 
    path = f'app/schema/migrations/{folder}'
    if version:
        version = version.replace('.', '_')
        if not version.startswith('v'):
            version = 'v' + version
        path = path + '/' + version
    return base_path(path)

def arkalos_path(path: str|None = None) -> str:
    '''Get a path relative to installed arkalos package root inside site-packages.'''
    this_files_dir = Path(__file__).parent.resolve()
    root_arkalos_dir = this_files_dir.parent.resolve()
    if path is None:
        path = ''
    return str(root_arkalos_dir.joinpath(path))

def find_folder_upwards(folder_name: str, starting_dir: str|None = None) -> str|None:
    '''
    Find the first folder with given name by searching upwards
    from the current file's directory.
    
    Args:
        folder_name: Name of the folder to find
        starting_dir: Directory to start searching from (defaults to current file's directory)
        
    Returns:
        Full path to the found folder or None if not found
    '''

    # If no starting directory provided, use the directory of the current file
    if starting_dir is None:
        starting_dir = os.path.dirname(os.path.abspath(__file__))
    
    current_dir = Path(starting_dir).absolute()
    
    # Keep going up until we find the folder or reach the filesystem root
    while True:
        # Check if target folder exists in current directory
        target_path = current_dir / folder_name
        if target_path.is_dir():
            return str(target_path)
        
        # Move up one directory
        parent_dir = current_dir.parent
        
        # If we've reached the root (parent is same as current)
        if parent_dir == current_dir:
            return None
            
        current_dir = parent_dir

def arkalos_templates_path() -> str:
    path = find_folder_upwards('templates')

    if not path:
        raise RuntimeError('Could not find Arkalos templates path')
    
    return path
    

def get_rel_path(path: str) -> str:
    '''Gets a relative path by removing the base path'''
    return path.replace(base_path(), '').lstrip('/')
