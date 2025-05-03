
import logging
import json
from datetime import datetime, timezone
import traceback
from dataclasses import dataclass, asdict

from arkalos.core.logger.format_exception import format_exception



@dataclass
class LogRecord:
    time: str
    src: str
    lvl: str
    msg: str
    data: str|None = None
    exc: str|None = None
    exc_msg: str|None = None
    exc_stck: str|None = None

class JsonFormatter(logging.Formatter):
    '''Formats log records as JSON Lines with UTC timezone'''

    DATE_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, max_traceback_frames = 3):
        super().__init__(datefmt=self.DATE_FMT)
        self.max_traceback_frames = max_traceback_frames

    def format(self, record):
        now = datetime.fromtimestamp(record.created, tz=timezone.utc)

        log_time = now.strftime(self.DATE_FMT)
        log_source = record.name
        log_level = record.levelname
        log_message = record.getMessage()

        log_entry = {
            'time': log_time,
            'src': log_source,
            'lvl': log_level,
            'msg': log_message
        }

        if record.exc_info:
            exc_type, exc_value, tb = record.exc_info
            log_exc = str(exc_type.__name__)
            log_exc_msg = str(exc_value)
            log_exc_stck = format_exception(record.exc_info, self.max_traceback_frames)

            log_entry['exc'] = log_exc
            log_entry['exc_msg'] = log_exc_msg
            log_entry['exc_stck'] = log_exc_stck


        if hasattr(record, 'extra_data') and record.extra_data:
            log_data = record.extra_data
            log_entry['data'] = log_data

        json_string = json.dumps(log_entry, default=str, ensure_ascii=False)

        return json_string
