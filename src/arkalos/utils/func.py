from functools import reduce, partial
from typing import Callable, Any

def pipe(*funcs: Callable[..., Any]) -> Callable[..., Any]:
    """Applies functions left to right with variable arguments."""
    def _pipe(*args, **kwargs):
        result = args
        for func in funcs:
            result = func(*result, **kwargs)
        return result
    return _pipe

def compose(*funcs: Callable[..., Any]) -> Callable[..., Any]:
    """Applies functions right to left with variable arguments."""
    def _compose(*args, **kwargs):
        result = args
        for func in reversed(funcs):
            result = func(*result, **kwargs)
        return result
    return _compose
