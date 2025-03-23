import re

def escape_filename(filename):
    # Remove characters that are invalid for filenames in most operating systems
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    return re.sub(invalid_chars, '_', filename)
