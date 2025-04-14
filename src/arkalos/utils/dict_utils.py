from typing import Any, cast, Type, Mapping, TypedDict
import copy
import re

def add_count_col(data, col):

    new_data = copy.deepcopy(data)

    # Count occurrences of each value
    value_counts = {}
    for item in new_data:
        value = item[col]
        value_counts[value] = value_counts.get(value, 0) + 1

    # Add the <col>_count to the original dictionary
    for item in new_data:
        value = item[col]
        item[f'{col}_count'] = value_counts[value]

    return new_data

def sort_by_col(data, columns, descending=False):
    """
    Sort a list of dictionaries by multiple columns with column-specific sort directions,
    supporting strings, numbers, and dates.
   
    Args:
        data (list): List of dictionaries to sort
        columns (str, list, or dict):
            - If str: Single column name to sort by
            - If list: Column names to sort by in order
            - If dict: Column names as keys and sort directions as values
              (True for descending, False for ascending)
        descending (bool, optional): Default sort direction if columns is str or list.
            True for descending, False for ascending. Defaults to False.
   
    Returns:
        list: A new sorted list of the dictionaries
    """
    # Convert all inputs to a standardized dictionary format
    sort_config = []
    if isinstance(columns, str):
        sort_config = [(columns, descending)]
    elif isinstance(columns, list):
        sort_config = [(col, descending) for col in columns]
    elif isinstance(columns, dict):
        sort_config = list(columns.items())
    
    # Sort in reverse order of columns (last column first)
    # This creates a stable sort that respects the column order
    sorted_data = data.copy()
    
    for col, is_descending in reversed(sort_config):
        sorted_data = sorted(sorted_data, 
                            key=lambda x: (x.get(col) is None, x.get(col)),
                            reverse=is_descending)
    
    return sorted_data

def sort_by_col_desc(data, columns):
    return sort_by_col(data, columns, True)

def filter_by_col(data: list, column: str, pattern: str) -> list:
    '''
    data must be a dict or TypedDict
    '''
    regex = re.compile(pattern, re.IGNORECASE)
    return [row for row in data if regex.search(row.get(column, ''))]
