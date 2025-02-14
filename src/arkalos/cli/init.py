import os
import shutil
import sys
import secrets
import re
from pathlib import Path

from arkalos.core.path import base_path, arkalos_path



RESET = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'



def is_initialized():
    return os.path.exists(base_path('app')) or os.path.exists(base_path('.env'))



def copy_starter_files(from_path, to_path):
    if not os.path.exists(from_path):
        print(RED + "ERROR: Starter folder does not exist." + RESET)
        return

    # Recursively copy the contents of the starter folder to the base path
    for item in os.listdir(from_path):
        source = os.path.join(from_path, item)
        destination = os.path.join(to_path, item)
        
        if os.path.isdir(source):
            shutil.copytree(source, destination, dirs_exist_ok=True)  # Overwrite existing dirs
        else:
            shutil.copy2(source, destination)  # Overwrite existing files

    print('1. Copied starter folder structure and files from starter template.')



def append_files(from_path, to_path):
    """
    Check for files in from_path that start with 'append_' and append their content
    to the corresponding file (with the 'append_' prefix removed) in to_path.
    
    For example, if from_path contains 'append_pyproject.toml' and to_path contains
    'pyproject.toml', the function will append the content of 'append_pyproject.toml'
    to the end of 'pyproject.toml'.
    """
    # List all files in from_path
    for filename in os.listdir(from_path):
        if filename.startswith("append_"):
            # The target filename is the remainder after "append_"
            target_filename = filename[len("append_"):]
            
            # Build the full paths for source and target files
            source_file = os.path.join(from_path, filename)
            target_file = os.path.join(to_path, target_filename)
            
            # Check if the target file exists
            if os.path.exists(target_file):
                # Read the content from the source file
                with open(source_file, 'r', encoding='utf-8') as src:
                    content_to_append = src.read()
                
                # Append the content to the target file
                with open(target_file, 'a', encoding='utf-8') as tgt:
                    # Optionally add a newline separator before appending
                    tgt.write("\n" + content_to_append)
                
                print(f"2. Appended content from '{GREEN}{filename}{RESET}' to '{GREEN}{target_filename}{RESET}'.")
            else:
                print(f"{YELLOW}Warning! Target file '{target_filename}' does not exist in '{to_path}'. Skipping.{RESET}")



def copy_env_example(proj_path):
    """
    Copies .env.example to .env in the specified directory.

    Args:
        proj_path (str): The path to the project directory.
    """
    env_example_path = os.path.join(proj_path, '.env.example')
    env_path = os.path.join(proj_path, '.env')

    if not os.path.isfile(env_example_path):
        raise FileNotFoundError(f"{RED}ERROR: No .env.example file found in {proj_path}{RESET}")

    try:
        shutil.copy(env_example_path, env_path)
        print(f"3. Copied {GREEN}.env.example{RESET} to {GREEN}.env{RESET}.")
    except Exception as e:
        print(f"{RED}ERROR: Failed to copy .env.example to .env: {e}{RESET}")



def set_env_file_contents(proj_path):
    """
    Updates the .env file with the project name from pyproject.toml and generates a secret key.

    Args:
        proj_path (str): The path to the project directory.
    """
    pyproject_path = os.path.join(proj_path, 'pyproject.toml')
    env_path = os.path.join(proj_path, '.env')

    if not os.path.isfile(pyproject_path):
        raise FileNotFoundError(f"{RED}ERROR: No pyproject.toml file found in {proj_path}{RESET}")
    if not os.path.isfile(env_path):
        raise FileNotFoundError(f"{RED}ERROR: No .env file found in {proj_path}. Make sure to copy .env.example first.{RESET}")

    with open(pyproject_path, 'r') as f:
        pyproject_contents = f.read()
    match = re.search(r'\[project\]\s*name\s*=\s*"([^"]+)"', pyproject_contents)
    if not match:
        raise ValueError("{RED}ERROR: Project name not found in pyproject.toml{RESET}")
    project_name = match.group(1)

    secret_key = 'base64:' + secrets.token_urlsafe(32)

    with open(env_path, 'r') as f:
        env_contents = f.read()
    env_contents = re.sub(r'APP_NAME=.*', f'APP_NAME={project_name}', env_contents)
    env_contents = re.sub(r'APP_KEY=.*', f'APP_KEY={secret_key}', env_contents)
    with open(env_path, 'w') as f:
        f.write(env_contents)

    print(f"4. Updated .env file and generated a secret app key.")



def move_files(proj_path):
    """
    Moves hello.py file to the scripts folder if it exists.

    Args:
        proj_path (str): The path to the project directory.
    """
    hello_path = os.path.join(proj_path, 'hello.py')
    scripts_dir = os.path.join(proj_path, 'scripts')

    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)

    if os.path.isfile(hello_path):
        shutil.move(hello_path, os.path.join(scripts_dir, 'hello.py'))
        print(f"5. Moved hello.py to scripts folder.")
    else:
        print(f"{YELLOW}Warning: hello.py not found.{RESET}")



def run():
    if is_initialized():
        print("Project is already initialized. Folders like 'app' or files like '.env' already exist.")
    else:

        starter_path = arkalos_path('templates/starter')
        starter_appends_path = arkalos_path('templates/starter_appends')
        proj_path = base_path()

        print()
        print(BLUE + "Initializing the new Arkalos project..." + RESET)
        print()
        copy_starter_files(starter_path, proj_path)
        append_files(starter_appends_path, proj_path)
        copy_env_example(proj_path)
        set_env_file_contents(proj_path)
        print()
        print(GREEN + "DONE. Initialization complete." + RESET)
        print()
        print()
