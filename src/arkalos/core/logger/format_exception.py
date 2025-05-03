
import os
import traceback

def format_exception(exc_info, max_traceback_frames):
    '''
    Format exception to show the last N frames, each on its own line.
    Uses module path instead of full file path.
    '''

    exc_type, exc_value, tb = exc_info
    
    # Extract the frames
    tb_frames = traceback.extract_tb(tb)
    
    # Get the last N frames (or fewer if there aren't enough)
    relevant_frames = tb_frames[-max_traceback_frames:] if len(tb_frames) >= max_traceback_frames else tb_frames
    
    # Format header
    result = f'{exc_type.__name__}: {exc_value}\n'
    result += 'Traceback (most recent call last):\n'
    
    # Format each frame on its own line
    for frame in relevant_frames:
        # Convert filename to module path when possible
        file_path = frame.filename
        
        # Try to convert to module notation
        if file_path.endswith('.py'):
            # Remove extension and convert slashes to dots
            module_path = file_path.replace('/', '.').replace('\\', '.')
            
            # Remove .py extension
            if module_path.endswith('.py'):
                module_path = module_path[:-3]
            
            # Handle common patterns to extract just the module path
            parts = module_path.split('.')
            if 'site-packages' in parts:
                # For installed packages: package.module
                idx = parts.index('site-packages')
                module_path = '.'.join(parts[idx+1:])
            elif 'dist-packages' in parts:
                # For distribution packages
                idx = parts.index('dist-packages')
                module_path = '.'.join(parts[idx+1:])
            elif len(parts) > 2:
                # For local modules: just use the module path without system paths
                # Try to find src or app directory as a root
                for root_dir in ['src', 'app', 'lib']:
                    if root_dir in parts:
                        idx = parts.index(root_dir)
                        module_path = '.'.join(parts[idx:])
                        break
        else:
            # If not a .py file, use the base filename
            module_path = os.path.basename(file_path)
        
        # Add class name to the function if it exists
        function_name = frame.name
        if '.' in function_name:
            module_path += f'.{function_name}'  # It's a class method
        else:
            module_path += f':{function_name}'
            
        # Add line number
        line_no = frame.lineno
        
        # Format frame line
        result += f'  {module_path}:{line_no}   >>>   {frame.line}\n'
    
    return result
