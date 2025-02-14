
from arkalos.core.registry import Registry
from arkalos.core.logger.logger import Logger
from arkalos.core.logger.file_logger import FileLogger

Registry.register('logger', FileLogger, True)

def logger() -> Logger:
    return Registry.get('logger')

def debug(message: str, data: dict = {}) -> None:
    logger().debug(message, data)

def info(message: str, data: dict = {}) -> None:
    logger().info(message, data)

def warning(message: str, data: dict = {}) -> None:
    logger().warning(message, data)

def error(message: str, data: dict = {}) -> None:
    logger().error(message, data)

def critical(message: str, data: dict = {}) -> None:
    logger().critical(message, data)
    