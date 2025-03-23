
import os
from datetime import datetime
import time
import logging
import json
import inspect

from arkalos.core.path import base_path
from arkalos.core.logger.logger import Logger, LogLevel



class FileLogger(Logger):

    def __init__(self) -> None:

        log_dir = base_path('data/logs')
        log_filename = f'arkalos-{datetime.now().strftime("%Y-%m")}.log'
        log_filepath = os.path.join(log_dir, log_filename)

        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            filename=log_filepath,
            filemode='a',
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.DEBUG
        )

        logging.Formatter.converter = time.gmtime

    def log(self, message: str, data: dict = {}, level: int = LogLevel.DEBUG) -> None:

        caller_frame = inspect.stack()[3]
        caller_module = caller_frame.frame.f_globals['__name__']
        caller_function = caller_frame.function
        
        full_message = f"{caller_module}.{caller_function}:\n{message}"
        
        if data:
            full_message = full_message + ' - ' + json.dumps(data)
            
        logging.log(msg=full_message + '\n', level=level)

