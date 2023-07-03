import sys
import time
from datetime import datetime, timedelta
from functools import wraps

from app.logger import log
import app.schema as s


def time_measurement(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        response_size = sys.getsizeof(result.json())
        total_time = end_time - start_time
        log(
            log.INFO,
            "Function [%s] %s took {%s} seconds and the json file is {%s} kb long",
            func.__name__,
            kwargs,
            str(total_time)[:5],
            response_size / 8000,
        )
        return result

    return wrapper


# Calculate the date of the most recent Thursday
def get_datetime_after_target_day_of_week(target_day: s.Weekday) -> datetime:
    today = datetime.now().date()
    current_day = today.weekday()
    days_ahead = (current_day - target_day.value) % 7
    return today - timedelta(days=days_ahead)
