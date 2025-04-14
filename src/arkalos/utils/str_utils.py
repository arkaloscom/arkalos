
import re



def snake(name: str) -> str:
    '''
    Convert camelCase or PascalCase to snake_case.
    Insert underscore before uppercase letters and lowercase the result.
    '''
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def after(string: str, substr: str) -> str:
    '''
    Returns everything after the given value in a string.
    '''
    return string.partition(substr)[2]
