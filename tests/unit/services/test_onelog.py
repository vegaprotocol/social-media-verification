from typing import Callable, Pattern
import pytest
from datetime import datetime, timezone
from decimal import Decimal
import re

from services.onelog import onelog, OneLog, onelog_json


def test_OneLog_basic():
    onelog = OneLog()

    assert onelog.to_single_line_key_value() == ""
    assert onelog.to_single_line_json() == "{}"

    onelog.info(string_val="my string")
    assert onelog.to_single_line_key_value() == 'string_val="my string"'
    assert onelog.to_single_line_json() == '{"string_val":"my string"}'

    onelog.info(int_val=123)
    assert (
        onelog.to_single_line_key_value()
        == 'string_val="my string", int_val="123"'
    )
    assert (
        onelog.to_single_line_json()
        == '{"string_val":"my string","int_val":123}'
    )

    onelog.info(float_val=1.23)
    assert (
        onelog.to_single_line_key_value()
        == 'string_val="my string", int_val="123", float_val="1.23"'
    )
    assert (
        onelog.to_single_line_json()
        == '{"string_val":"my string","int_val":123,"float_val":1.23}'
    )


def test_OneLog_special_values():

    # date
    onelog = OneLog(date_val=datetime(2020, 10, 15, 10, 21, 33))
    assert (
        onelog.to_single_line_key_value() == 'date_val="2020-10-15T10:21:33"'
    )
    assert onelog.to_single_line_json() == '{"date_val":"2020-10-15T10:21:33"}'

    # json
    onelog = OneLog(json_val={"key": "val"})
    assert (
        onelog.to_single_line_key_value() == 'json_val="{\\"key\\":\\"val\\"}"'
    )
    assert onelog.to_single_line_json() == '{"json_val":{"key":"val"}}'

    # json with date
    onelog = OneLog(json_date_val={"date": datetime(2020, 10, 15, 10, 21, 33)})
    assert (
        onelog.to_single_line_key_value()
        == 'json_date_val="{\\"date\\":\\"2020-10-15T10:21:33\\"}"'
    )
    assert (
        onelog.to_single_line_json()
        == '{"json_date_val":{"date":"2020-10-15T10:21:33"}}'
    )

    # escape new lines
    onelog = OneLog(new_line="this\nis\nnewline\ntest")
    assert (
        onelog.to_single_line_key_value()
        == 'new_line="this\\nis\\nnewline\\ntest"'
    )
    assert (
        onelog.to_single_line_json()
        == '{"new_line":"this\\nis\\nnewline\\ntest"}'
    )

    # handle Decimal into string
    onelog = OneLog(decimal_val=Decimal("1.32"))
    assert onelog.to_single_line_key_value() == 'decimal_val="1.32"'
    assert onelog.to_single_line_json() == '{"decimal_val":"1.32"}'


@pytest.mark.parametrize(
    "onelog_decorator, log_regex",
    [
        (
            onelog,
            r'^time="([^"]*)", action="inner_function", '
            r'inner="value", time_ms="0", status="SUCCESS"$',
        ),
        (
            onelog_json,
            r'^{"time":"([^"]*)","action":"inner_function",'
            r'"inner":"value","time_ms":0,"status":"SUCCESS"}$',
        ),
    ],
)
def test_onelog_decorator(
    onelog_decorator: Callable[[Callable], Callable],
    log_regex: Pattern,
    capsys,
):
    @onelog_decorator
    def inner_function(onelog: OneLog = None):
        onelog.info(inner="value")

    # execute
    time_before = datetime.utcnow().replace(tzinfo=timezone.utc)
    inner_function()
    time_after = datetime.utcnow().replace(tzinfo=timezone.utc)

    # validate log output
    captured = capsys.readouterr()

    matched = re.match(log_regex, captured.out)
    assert matched
    log_timestamp = datetime.fromisoformat(matched.group(1))
    assert time_before <= log_timestamp and log_timestamp <= time_after


@pytest.mark.parametrize(
    "onelog_decorator, log_regex",
    [
        (
            onelog,
            r'^time="([^"]*)", action="exception_inner_function", '
            r'before="exception", '
            r'err="test error", time_ms="0", status="FAILED"$',
        ),
        (
            onelog_json,
            r'^{"time":"([^"]*)","action":"exception_inner_function",'
            r'"before":"exception",'
            r'"err":"test error","time_ms":0,"status":"FAILED"}$',
        ),
    ],
)
def test_onelog_decorator_exception(
    onelog_decorator: Callable[[Callable], Callable],
    log_regex: Pattern,
    capsys,
):
    @onelog_decorator
    def exception_inner_function(onelog: OneLog = None):
        onelog.info(before="exception")
        raise TypeError("test error")

    # execute
    with pytest.raises(TypeError):
        exception_inner_function()

    # validate log output
    captured = capsys.readouterr()

    assert re.match(log_regex, captured.out)
