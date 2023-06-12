from app.logger import log

from functools import wraps
import time


def time_measurement(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        log(
            log.INFO,
            "Function [%s] %s took {%s} seconds",
            func.__name__,
            kwargs,
            str(total_time)[:5],
        )
        return result

    return wrapper
