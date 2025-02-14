from typing import Dict, Type, Callable, Any

class Registry:
    __store: Dict[str, Any] = {}
    __instances: Dict[str, Any] = {}

    @classmethod
    def register(cls, key: str, value: Any, is_global: bool = True):
        cls.__store[key] = (value, is_global)

    @classmethod
    def get(cls, key: str) -> Any:
        value, singleton = cls.__store[key]
        if isinstance(value, type):
            # If a class
            if singleton:
                # If a global class (singleton) with only one instance
                if key not in cls.__instances:
                    cls.__instances[key] = value()
                # Get a single global instance
                return cls.__instances[key]
            # Create a new object instance each time
            return value()
        # a function
        return value
