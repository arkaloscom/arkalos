import os
import sys
import re
from pathlib import Path

from arkalos.core.path import arkalos_templates_path, base_path

def convert_to_snake_case(name):
    """Convert a CamelCase or PascalCase name to snake_case"""
    # Handle case where input is already snake_case
    if '_' in name and name.lower() == name:
        return name
    
    # Replace capital letters with underscore + lowercase letter
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def convert_to_pascal_case(name):
    """Convert any case format to PascalCase"""
    # First convert to snake_case if not already
    snake_case = convert_to_snake_case(name)
    # Convert snake_case to PascalCase
    return ''.join(word.capitalize() for word in snake_case.split('_'))

def run():
    if len(sys.argv) < 3:
        print("Error: Please provide a middleware name.")
        print("Usage: uv run arkalos make:mw <MiddlewareName>")
        return
    
    # Get middleware name from command-line argument
    middleware_name = sys.argv[2]
    
    class_name = f"{convert_to_pascal_case(middleware_name)}Middleware"
    file_name = f"{convert_to_snake_case(middleware_name)}_middleware.py"
    
    # Get template and destination paths
    template_file = Path(arkalos_templates_path()) / 'make' / 'middleware.py'
    destination_dir = Path(base_path('app/http/middleware'))
    destination_file = destination_dir / file_name
    
    os.makedirs(destination_dir, exist_ok=True)
    if destination_file.exists():
        print(f"Error: File '{file_name}' already exists.")
        return
    
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Replace placeholder with actual class name
    new_content = template_content.replace('MAKEMiddleware', class_name)
    
    with open(destination_file, 'w') as f:
        f.write(new_content)
    
    print(f"Middleware created successfully: {destination_file}")
    print(f"Class name: {class_name}")
