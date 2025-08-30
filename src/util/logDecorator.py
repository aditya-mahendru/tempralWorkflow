from functools import wraps
from loguru import logger

def ioLogger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Starting {func.__name__} with args: {args} and kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            result_str = str(result)
            if len(result_str) > 100:
                result_str = result_str[:100] + "..."
                logger.debug(f"Result too long, truncated to: {result_str}")
            else:
                logger.debug(f"Finished {func.__name__} with result: {result_str}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise e
    return wrapper