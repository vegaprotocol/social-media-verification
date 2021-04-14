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
            self.log_entries[key] = value

    def to_single_line_json(self) -> str:
        return json.dumps(
            self.log_entries,
            default=json_serial,  # properly convert dates
            separators=(",", ":"),  # remove whitespaces and \n
            ensure_ascii=False,  # UTF8
        )

    def to_single_line_key_value(self) -> str:
        kv = []
        for key, value in self.log_entries.items():
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            elif isinstance(value, (Decimal, int, float)):
                value = str(value)
            elif not isinstance(value, str):
                value = json.dumps(
                    value,
                    default=json_serial,  # properly convert dates
                    separators=(",", ":"),  # remove whitespaces and \n
                    ensure_ascii=False,  # UTF8
                )
            value = value.replace('"', '\\"').replace("\n", "\\n")
            kv.append(f'{key!s}="{value!s}"')

        return ", ".join(kv)


def _onelog(
    f: Callable,
    onelog_to_single_line: Callable[[OneLog], None],
    log: Callable[[str], None],
) -> Callable:
    def wrapper(*args, **kwargs):
        onelog = OneLog(
            time=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            action=f.__name__,
        )
        start_time = timer()
        try:
            return f(*args, **kwargs, onelog=onelog)
        except Exception as err:
            onelog.info(err=str(err))
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
            log(onelog_to_single_line(onelog))

    return wrapper


def onelog(f: Callable):
    """`@onelog` decorator produces one log in single line for a decorated function

    Usage:
    ```
    @onelog
    def my_handler(request, onelog: OneLog):
        ...
        onelog.info(client_id=request.client_id)
        ...
        onelog.info(item_count=len(items), max_price=max(item_prices))
        ...
    ```
    will produce log:
    ```
    time="2021-04-08T20:59:12.143317+00:00", action="my_handler",
    client_id="1", item_count="12", max_price="34.99", time_ms="291",
    status="SUCCESS"
    ```
    """
    return _onelog(f, OneLog.to_single_line_key_value, print)


def onelog_json(f: Callable):
    """`@onelog_json` decorator produces one log in single line for
    a decorated function.

    Note: Format of produced log is json (i.e. one json in a single line)

    Usage:
    ```
    @onelog_json
    def my_handler(request, onelog: OneLog):
        ...
        onelog.info(client_id=request.client_id)
        ...
        onelog.info(item_count=len(items), max_price=max(item_prices))
        ...
    ```
    will produce log:
    ```
    {"time":"2021-04-08T20:59:12.143317+00:00","action":"my_handler","client_id":1,"item_count":12,"max_price":"34.99","time_ms":"291","status":"SUCCESS"
    ```
    """
    return _onelog(f, OneLog.to_single_line_json, print)
