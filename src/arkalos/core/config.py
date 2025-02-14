from typing import Optional
import importlib
import json
from arkalos.core.registry import Registry

def __config(key: str, default: Optional[str]=None):
    """
    Access configuration values from files in the `config` directory.

    Args:
        key (str): Dot-separated key to the config value (e.g., 'app.name' or 'data_sources.airtable.tables[name]').

    Returns:
        Any: The corresponding configuration value, or raises an error if not found.
    """
    # Check if the key contains collection syntax (e.g., '[name]')
    if '[' in key and ']' in key:
        base_key, collection_key = key.split('[', 1)
        collection_key = collection_key.rstrip(']')  # Remove the trailing ']'
    else:
        base_key, collection_key = key, None

    parts = base_key.split('.')
    if len(parts) < 2:
        raise ValueError("Invalid config key. Use the format 'module.key' (e.g., 'app.name').")

    module_name, config_key = parts[0], '.'.join(parts[1:])
    try:
        # Dynamically import the module from the root-level `config` directory
        module = importlib.import_module(f"config.{module_name}")
    except ModuleNotFoundError:
        if (default):
            return default
        raise ModuleNotFoundError(f"Config module '{module_name}' not found in the 'config' directory.")

    # Ensure the module has a `config` dictionary
    if not hasattr(module, 'config'):
        raise AttributeError(f"Module 'config.{module_name}' does not have a 'config' dictionary.")

    config_dict = getattr(module, 'config')

    # Traverse the dictionary to find the nested key
    keys = config_key.split('.')
    value = config_dict
    for k in keys:
        if k in value:
            value = value[k]
        else:
            if (default):
                return default
            raise KeyError(f"Key '{config_key}' not found in 'config.{module_name}'.")

    # If collection syntax is used, collect the specified keys
    if collection_key:
        if not isinstance(value, list):
            raise TypeError(f"Expected a list at '{config_key}', but got {type(value).__name__}.")
        try:
            return [item[collection_key] for item in value]
        except KeyError:
            raise KeyError(f"Key '{collection_key}' not found in items of '{config_key}'.")
        
    # If the value is a JSON string, try parsing it into a Python object
    if isinstance(value, str):
        try:
            parsed_value = json.loads(value)
            return parsed_value
        except json.JSONDecodeError:
            # If parsing fails, return the value as is
            return value

    return value

Registry.register('config', __config)

def config(key: str, default: Optional[str]=None):
    return Registry.get('config')(key, default)
