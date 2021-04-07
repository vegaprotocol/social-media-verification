import pytest
from datetime import datetime, timezone
from decimal import Decimal
import re

from smv.helpers.onelog import onelog, OneLog


def test_OneLog_basic():
    onelog = OneLog()

    assert onelog.to_single_line() == ""

    onelog.info(string_val="my string")
    assert onelog.to_single_line() == 'string_val="my string"'

    onelog.info(int_val=123)
    assert onelog.to_single_line() == 'string_val="my string", int_val="123"'

    onelog.info(float_val=1.23)
    assert onelog.to_single_line() == 'string_val="my string", int_val="123", float_val="1.23"'


@pytest.mark.parametrize("description, value, expected_log", [
    ("date", datetime(2020, 10, 15, 10, 21, 33), 'val="2020-10-15T10:21:33"'),
    ("json", {"key": "val"}, 'val="{\\"key\\":\\"val\\"}"'),
    (   "json date",
        {"date": datetime(2020, 10, 15, 10, 21, 33)},
        'val="{\\"date\\":\\"2020-10-15T10:21:33\\"}"',
    ),
    ("new line", "this\nis\nnewline", 'val="this\\nis\\nnewline"'),
    ("decimal", Decimal("1.32"), 'val="1.32"')

])
def test_OneLog_special_values(description, value, expected_log):
    onelog = OneLog(val=value)

    assert onelog.to_single_line() == expected_log, f"Failed: {description}"


def test_onelog_decorator(capsys):
    @onelog
    def inner_function(onelog: OneLog = None):
        onelog.info(inner="value")

    # execute
    time_before = datetime.utcnow().replace(tzinfo=timezone.utc)
    inner_function()
    time_after = datetime.utcnow().replace(tzinfo=timezone.utc)

    # validate log output
    captured = capsys.readouterr()

    matched = re.match(r'^time="([^"]*)", action="inner_function", inner="value", time_ms="0", status="SUCCESS"$', captured.out)
    assert matched
    log_timestamp = datetime.fromisoformat(matched.group(1))
    assert   time_before <= log_timestamp and log_timestamp <= time_after


def test_onelog_decorator_exception(capsys):
    @onelog
    def exception_inner_function(onelog: OneLog = None):
        raise TypeError('test error')

    # execute
    with pytest.raises(TypeError):
        exception_inner_function()

    # validate log output
    captured = capsys.readouterr()

    assert re.match(r'^time="([^"]*)", action="exception_inner_function", time_ms="0", status="FAILED"$', captured.out)
