
from arkalos.core.registry import Registry
from arkalos.core.logger.logger import Logger

Registry.register('logger', Logger, True)

def logger() -> Logger:
    return Registry.get('logger')

def log(message: str, data: dict = {}, level: int = Logger.L.INFO) -> None:
    logger().log(message, data, level)

def debug(message: str, data: dict = {}) -> None:
    logger().debug(message, data)

def access(message: str, data: dict = {}) -> None:
    logger().access(message, data)

def info(message: str, data: dict = {}) -> None:
    logger().info(message, data)

def warning(message: str, data: dict = {}) -> None:
    logger().warning(message, data)

def error(message: str, data: dict = {}) -> None:
    logger().error(message, data)

def critical(message: str, data: dict = {}) -> None:
    logger().critical(message, data)
    
def exception(message: str|BaseException, data: dict = {}) -> None:
    logger().exception(message, data)
