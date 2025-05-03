
from typing import Any, Literal
import logging
import os
from datetime import datetime

from arkalos.core.path import base_path
from arkalos.core.config import config
from arkalos.utils.file_utils import FileReader

from arkalos.core.logger.log_level import LogLevel
from arkalos.core.logger.console_formatter import ConsoleFormatter
from arkalos.core.logger.json_formatter import JsonFormatter
from arkalos.core.logger.info_filter import InfoFilter
from arkalos.core.logger.file_handler import FileHandler



class Logger:
    '''
    Unified logging interface for application and third-party logs.
    Automatically separates logs by severity into different files.
    '''

    L: type[LogLevel] = LogLevel

    def __init__(
        self, 
        name='arkalos',
        log_dir=base_path('data/logs'),
        level=LogLevel.DEBUG if config('app.debug', 'False') else LogLevel.ACCESS,
        max_traceback_frames=10
    ):
        '''
        Initialize logger with configuration.
        
        Args:
            name: Root logger name
            log_dir: Directory to store log files
            level: Minimum log level to capture
            console_format: Format string for console output (optional)
            file_format: Format string for file output (optional)
            use_colors: Whether to use colored output in console
            max_traceback_frames: Number of frames to show in tracebacks
        '''
        self.name = name
        self.log_dir = log_dir
        self.level = level
        self.max_traceback_frames = max_traceback_frames

        file_ext = '.jsonl'
        
        # Create log file paths based on current month
        date_suffix = datetime.now().strftime('%Y-%m')
        self.log_info_file = os.path.join(self.log_dir, f'{self.name}-{date_suffix}-info{file_ext}')
        self.log_err_file = os.path.join(self.log_dir, f'{self.name}-{date_suffix}-error{file_ext}')
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up the logger
        self._setup()
        
    def _setup(self):
        '''Configure the logging system.'''

        # Register custom levels
        logging.addLevelName(LogLevel.ACCESS, 'ACCESS')
        
        # Get the root logger for our application
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = JsonFormatter(
            max_traceback_frames=self.max_traceback_frames
        )
        console_formatter = ConsoleFormatter(
            max_traceback_frames=self.max_traceback_frames
        )
        
        # Create handlers
        handlers = self._createHandlers(file_formatter, console_formatter)
        
        # Add handlers to logger
        for handler in handlers:
            self.logger.addHandler(handler)

    def _createHandlers(self, file_formatter, console_formatter):
        '''Create and configure log handlers.'''
        
        # Handler for info, debug, and access logs (writes JSON)
        info_handler = FileHandler(self.log_info_file, encoding='utf-8')
        info_handler.setFormatter(file_formatter)
        info_handler.setLevel(logging.DEBUG)
        info_handler.addFilter(InfoFilter())
        
        # Handler for warning, error, and critical logs (writes JSON)
        error_handler = FileHandler(self.log_err_file, encoding='utf-8')
        error_handler.setFormatter(file_formatter)
        error_handler.setLevel(logging.WARNING)
        
        # Console handler for all logs (uses colored formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.level)
        
        return [info_handler, error_handler, console_handler]

    def getLogger(self, name=None):
        '''
        Get a logger instance for a specific component.
        
        Args:
            name: Logger name (will be prefixed with the root logger name)
            
        Returns:
            Configured logger instance
        '''
        
        if name:
            return logging.getLogger(f'{self.name}.{name}')
        return self.logger
    
    def log(self, msg, data=None, level=LogLevel.INFO, exc_info=False):
        '''
        Log a message with structured data.
        
        Args:
            msg: Log message
            data: Additional structured data to include
            level: Log level (defaults to INFO)
        '''

        extra_data = {'extra_data': data} if data else None
        
        self.logger.log(level, msg, extra=extra_data, exc_info=exc_info)
    
    # Convenience methods that call the main log method
    def debug(self, msg, data=None): 
        self.log(msg, data, LogLevel.DEBUG)

    def access(self, msg, data=None): 
        self.log(msg, data, LogLevel.ACCESS)
        
    def info(self, msg, data=None):
        self.log(msg, data, LogLevel.INFO)
        
    def warning(self, msg, data=None):
        self.log(msg, data, LogLevel.WARNING)
        
    def error(self, msg, data=None):
        self.log(msg, data, LogLevel.ERROR)
        
    def critical(self, msg, data=None):
        self.log(msg, data, LogLevel.CRITICAL)
        
    def exception(self, msg, data=None):
        '''Log an exception message with traceback.'''
        
        self.log(msg, data, LogLevel.ERROR, exc_info=True)

    def getUvicornLogConfig(self):
        '''
        Get a Uvicorn-compatible logging configuration.
        Use this when starting the Uvicorn server.
        '''
        
        uv_level = LogLevel.INFO if self.level == LogLevel.DEBUG else self.level
        watch_level = LogLevel.WARNING if self.level < LogLevel.WARNING else self.level

        # Define external loggers with their levels
        external_loggers = {
            'uvicorn': uv_level,
            'uvicorn.error': uv_level,
            'uvicorn.access': uv_level,
            'uvicorn.asgi': uv_level,
            'watchfiles.main': watch_level,
            'watchfiles.cli': watch_level,
            'fastapi': uv_level
        }
        
        # Build logger configurations
        loggers_config = {
            # Root logger
            '': {
                'handlers': ['console', 'info_file', 'error_file'],
                'level': self.level,
            },
            # Main application logger
            self.name: {
                'handlers': ['console', 'info_file', 'error_file'],
                'level': self.level,
                'propagate': False,
            }
        }
        
        # Add external loggers
        for logger_name, level in external_loggers.items():
            loggers_config[logger_name] = {
                'handlers': ['console', 'info_file', 'error_file'],
                'level': level,
                'propagate': False, # Prevent duplicates
            }

        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'console': {
                    '()': ConsoleFormatter,
                    'max_traceback_frames': self.max_traceback_frames
                },
                'json_file': {
                    '()': JsonFormatter,
                    'max_traceback_frames': self.max_traceback_frames
                }
            },
            'filters': {
                'info_filter': {
                    '()': InfoFilter,
                }
            },
            'handlers': {
                'console': {
                    'class': logging.StreamHandler,
                    'formatter': 'console',
                    'level': self.level,
                },
                'info_file': {
                    'class': FileHandler,
                    'formatter': 'json_file',
                    'filename': self.log_info_file,
                    'encoding': 'utf-8',
                    'filters': ['info_filter'],
                },
                'error_file': {
                    'class': FileHandler,
                    'formatter': 'json_file',
                    'filename': self.log_err_file,
                    'encoding': 'utf-8',
                    'level': 'WARNING',
                },
            },
            'loggers': loggers_config,
        }

    def readLog(self, 
        type: Literal['error']|Literal['info'] = 'error',
        month: str|None = None,
        page: int = 1, 
        page_size: int = 50
    ) -> list[dict[str, Any]]|bool:
        '''
        Reads the latest logs from a JSON Lines file (.jsonl).

        Args:
            type (str): Log file type (error or info)
            month (str): The month in YYYY-MM format, i.e. 2025-05.
            page (int): The page number to read, starting from 1 for the most recent page.
            page_size (int): The number of lines per page.

        Returns:
            list[dict[str, Any]]|bool: A list of log objects or False if the file doesn't exist.
        '''

        if not month:
            month = datetime.now().strftime("%Y-%m")

        file_path = base_path(f"data/logs/arkalos-{month}-{type}.jsonl")
        reader = FileReader(file_path)
        
        if not reader.exists():
            return False
            
        reader.countPages(page_size=page_size)
        return reader.getJSONPage(page=page, page_size=page_size, reverse=True)

    def readLogCountPages(self, 
        type: Literal['error']|Literal['info'] = 'error',
        month: str|None = None,
        page_size: int = 50
    ) -> int:
        '''
        Get the total number of pages for particular JSONL log file

        Args:
            type (str): Log file type (error or info)
            month (str): The month in YYYY-MM format, i.e. 2025-05.
            page_size (int): The number of lines per page.

        Returns:
            int: Page count.
        '''

        if not month:
            month = datetime.now().strftime("%Y-%m")

        file_path = base_path(f"data/logs/arkalos-{month}-{type}.jsonl")
        reader = FileReader(file_path)
        
        if not reader.exists():
            return False
            
        return reader.countPages(page_size=page_size)
