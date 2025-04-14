
import re
import os



def escape_filename(filename):
    # Remove characters that are invalid for filenames in most operating systems
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    return re.sub(invalid_chars, '_', filename)

def create_folder(file_path_name):
    folder_path = os.path.dirname(file_path_name)
    os.makedirs(folder_path, exist_ok=True)
