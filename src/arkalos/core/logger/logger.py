
from abc import ABC, abstractmethod
import os
import logging
from datetime import datetime
import time
import json

from arkalos.core.path import base_path
from arkalos.core.registry import Registry



class LogLevel:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL



class Logger(ABC):

    LEVEL: type[LogLevel] = LogLevel

    @abstractmethod
    def __init__(self) -> None:
        """Set up the logging configuration."""
        pass

    @abstractmethod
    def log(self, message: str, data: dict = {}, level: int = LogLevel.DEBUG) -> None:
        """Log a message with a specified severity level."""
        pass

    def debug(self, message: str, data: dict = {}) -> None:
        self.log(message, data, LogLevel.DEBUG)

    def info(self, message: str, data: dict = {}) -> None:
        self.log(message, data, LogLevel.INFO)

    def warning(self, message: str, data: dict = {}) -> None:
        self.log(message, data, LogLevel.WARNING)

    def error(self, message: str, data: dict = {}) -> None:
        self.log(message, data, LogLevel.ERROR)

    def critical(self, message: str, data: dict = {}) -> None:
        self.log(message, data, LogLevel.CRITICAL)
