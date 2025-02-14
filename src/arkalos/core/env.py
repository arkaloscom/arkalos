import os
from typing import Any, TypeVar, Optional
from dotenv import load_dotenv


from arkalos.core.path import base_path

T = TypeVar('T')

def env(key: str, default: Optional[T] = None) -> Any:

    load_dotenv(dotenv_path=base_path('.env'), override=True)

    value = os.getenv(key, default)
    
    # Handle boolean values
    if isinstance(value, str):
        if value.lower() in ('true', '1', 'yes'):
            return True
        if value.lower() in ('false', '0', 'no'):
            return False
    
    return value
