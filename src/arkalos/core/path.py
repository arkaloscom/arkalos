
from pathlib import Path
from functools import lru_cache

_PROJECT_ROOT: Path|None = None

@lru_cache()
def _get_project_root() -> Path:
    """Get the project root path, caching the result"""
    global _PROJECT_ROOT
    
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT
        
    # Start from the current working directory
    current = Path.cwd()
    while current != current.parent:
        # Look for markers that indicate project root
        if any((current / marker).exists() for marker in ['pyproject.toml', '.env', '.git']):
            _PROJECT_ROOT = current
            return current
        current = current.parent
        
    raise RuntimeError("Could not find project root")

def base_path(*parts: str) -> str:
    """Get a path relative to project root"""
    return str(_get_project_root().joinpath(*parts))

def arkalos_path(*parts: str) -> str:
    """Get a path relative to installed arkalos package root inside site-packages"""
    return str(Path(__file__).parent.parent.joinpath(*parts))
