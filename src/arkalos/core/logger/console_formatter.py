
import logging
import json
import os
import traceback

from arkalos.core.logger.log_level import LogLevel
from arkalos.core.logger.format_exception import format_exception


class ConsoleFormatter(logging.Formatter):
    '''
    Unified log formatter that handles text formatting, colors, and exception formatting
    for CONSOLE output.
    Functionality is separated into distinct methods for better organization.
    '''

    # Default format strings
    CONSOLE_FORMAT = '%(message)s' # Base format for console
    FILE_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s' # Kept for reference, not used by this formatter directly

    # ANSI color codes
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    def __init__(self, max_traceback_frames=3):
        '''
        Initialize the formatter with options.

        Args:
            fmt: Format string for log messages (primarily for message part)
            use_colors: Whether to use colored output (intended for console)
            max_traceback_frames: Number of traceback frames to show
        '''
        super().__init__(fmt=self.CONSOLE_FORMAT)
        self.max_traceback_frames = max_traceback_frames

    def format(self, record):
        '''Format log record with color and exception handling for console.'''
        record.message = record.getMessage()

        # Apply color prefix if enabled
        prefix = self._getColoredPrefix(record.levelno)

        # Handle exception formatting if present
        exc_text = ''
        if record.exc_info:
            # Use the custom exception formatter
            exc_text = format_exception(record.exc_info, self.max_traceback_frames)
            # Ensure exception text starts on a new line if message exists
            if record.message:
                 exc_text = f"\n{exc_text}"

        # Combine prefix, message, and exception text
        log_output = f"{prefix} {record.message}{exc_text}"

        # Add extra data if present (simple string representation for console)
        if hasattr(record, 'extra_data') and record.extra_data:
             try:
                 extra_str = json.dumps(record.extra_data, default=str, ensure_ascii=False)
                 log_output += f" | {extra_str}"
             except Exception:
                 log_output += " | [Unserializable extra data]" # Fallback

        return log_output

    def _getColoredPrefix(self, level):
        '''Get colored prefix for log level.'''
        color = ''
        is_bold = False

        if level == LogLevel.DEBUG:
            color = self.BLUE
        elif level == LogLevel.ACCESS:
            color = self.GREEN # Or choose another color for access
        elif level == LogLevel.INFO:
            color = self.GREEN
        elif level == LogLevel.WARNING:
            color = self.YELLOW
        elif level == LogLevel.ERROR:
            color = self.RED
        elif level == LogLevel.CRITICAL:
            color = self.RED
            is_bold = True

        prefix = f"{logging.getLevelName(level):<10}"
        bold_code = self.BOLD if is_bold else ''
        return f'{bold_code}{color}{prefix}{self.RESET}'


    def _formatException(self, exc_info):
        '''
        Format exception to show the last N frames, each on its own line.
        Uses module path instead of full file path.
        '''
        exc_type, exc_value, tb = exc_info

        # Extract the frames
        tb_frames = traceback.extract_tb(tb)

        # Get the last N frames (or fewer if there aren't enough)
        relevant_frames = tb_frames[-self.max_traceback_frames:] if len(tb_frames) >= self.max_traceback_frames else tb_frames

        # Format header
        # Use traceback.format_exception_only for a standard representation
        exception_only = traceback.format_exception_only(exc_type, exc_value)
        result = "".join(exception_only).strip() + '\n' # Get exception type and value
        result += '  Traceback (most recent call last):\n'

        # Format each frame on its own line
        for frame in relevant_frames:
            # Convert filename to module path when possible
            file_path = frame.filename

            # Try to convert to module notation
            module_path_str = file_path # Default to full path
            if file_path.endswith('.py'):
                # Remove extension and convert slashes to dots
                module_path = file_path.replace('/', '.').replace('\\', '.')

                # Remove .py extension
                if module_path.endswith('.py'):
                    module_path = module_path[:-3]

                # Handle common patterns to extract just the module path
                # (This part might need adjustment based on your project structure)
                parts = module_path.split('.')
                found_root = False
                for root_dir in ['arkalos', 'src', 'app', 'lib', 'site-packages', 'dist-packages']:
                     if root_dir in parts:
                         idx = parts.index(root_dir)
                         # For site-packages/dist-packages, take everything after
                         # For project dirs, include the root dir itself
                         start_index = idx + 1 if root_dir in ['site-packages', 'dist-packages'] else idx
                         module_path_str = '.'.join(parts[start_index:])
                         found_root = True
                         break
                if not found_root and len(parts) > 1:
                     # Fallback for local modules not under known roots (e.g., scripts)
                     module_path_str = '.'.join(parts[-2:]) # Take last two parts as guess

            else:
                # If not a .py file, use the base filename
                module_path_str = os.path.basename(file_path)

            # Add function name
            function_name = frame.name

            # Add line number
            line_no = frame.lineno

            # Format frame line
            result += f'    File "{module_path_str}", line {line_no}, in {function_name}\n'
            # Include the source code line if available
            if frame.line:
                 result += f'      {frame.line.strip()}\n'

        # Remove trailing newline if any
        return result.strip()


