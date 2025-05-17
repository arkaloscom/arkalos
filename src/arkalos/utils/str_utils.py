
import re



def snake(string: str) -> str:
    '''
    Convert camelCase or PascalCase to snake_case.
    Insert underscore before uppercase letters and lowercase the result.
    '''
    string = string.strip().replace(' ', '_')
    
    parts = string.split('_')
    processed_parts = []

    for part in parts:
        if not part:
            continue
        # Step 3: Insert underscores between lowercase-uppercase and uppercase-uppercase-lowercase transitions
        processed = re.sub(
            r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', 
            '_', 
            part
        )
        processed_parts.append(processed.lower())

    return '_'.join(processed_parts)



def after(string: str, substr: str) -> str:
    '''
    Returns everything after the given value in a string.
    '''
    return string.partition(substr)[2]



def truncate(string: str, max_length: int|None = None) -> str:
    '''
    Truncate a string to a given length.
    '''
    if max_length is not None and len(string) > max_length:
        return string[:max_length].rstrip('_- ')
    return string



def limit(text: str, max_length: int, suffix: str = '...', preserve_words: bool = False) -> str:
    '''
    Truncate a string to a given length with a suffix while optionally preserving whole words.
    
    Args:
        text (str): The input string to truncate.
        max_length (int): The maximum allowed length of the result.
        suffix (str): String to append at the end of the truncated string.
        preserve_words (bool): If True, truncate at the nearest word boundary.
    
    Returns:
        str: Truncated string with optional suffix.
    '''

    if not text or len(text) <= max_length:
        return text

    if not preserve_words:
        return text[:max_length].rstrip() + suffix

    # Normalize newlines to spaces and strip HTML-like tags
    value = re.sub(r'[\n\r]+', ' ', text)
    value = re.sub(r'<[^>]+>', '', value)
    value = re.sub(r'\s{2,}', ' ', value).strip()

    truncated = value[:max_length].rstrip()

    if len(value) > max_length and value[max_length] == ' ':
        return truncated + suffix
    else:
        # Remove the last partial word
        return re.sub(r'\s\S*$', '', truncated) + suffix