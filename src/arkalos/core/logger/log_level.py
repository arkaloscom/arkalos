
from enum import IntEnum
import logging



class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    ACCESS = 15
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
