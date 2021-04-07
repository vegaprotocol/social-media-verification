from typing import Callable
from collections import OrderedDict
from datetime import date, datetime, timezone
import json
from timeit import default_timer as timer
from decimal import Decimal


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


class OneLog(object):
    def __init__(self, **kwargs) -> None:
        self.log_entries = OrderedDict()
        self.info(**kwargs)
    
    def info(self, **kwargs):
        for key, value in kwargs.items():
            if not isinstance(value, str):
                if isinstance(value, (datetime, date)):
                    value = value.isoformat()
                elif isinstance(value, (Decimal, int)):
                    value = str(value)
                else:
                    value = json.dumps(
                        value,
                        default=json_serial,  # properly convert dates
                        separators=(',', ':'),  # remove whitespaces and newlines
                        ensure_ascii=False,  # UTF8
                    )
            value = value.replace('"','\\"').replace("\n", "\\n")
            self.log_entries[key] = value
    
    def to_single_line(self):
        return ', '.join(f'{key!s}="{val!s}"' for (key,val) in self.log_entries.items())


def onelog(f: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        onelog = OneLog(
            time=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            action=f.__name__,
        )
        start_time = timer()
        try:
            return f(*args, **kwargs, onelog=onelog)
        except Exception:
            if "status" not in onelog.log_entries:
                onelog.info(status="FAILED")
            raise  # rethrow exception
        finally:
            end_time = timer()
            onelog.info(time_ms=int((end_time - start_time) * 1000))
            if "status" not in onelog.log_entries:
                onelog.info(status="SUCCESS")
            else:
                onelog.log_entries.move_to_end("status")
            print(onelog.to_single_line())
    return wrapper
