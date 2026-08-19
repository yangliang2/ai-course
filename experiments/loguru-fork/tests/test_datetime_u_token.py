"""Tests for the fork-specific "u" time token (seconds since midnight + precision)."""

import pytest

import loguru
from loguru import logger
from loguru._datetime import _compile_format
import loguru._internal_config as _cfg


@pytest.mark.parametrize(
    ("precision", "expected"),
    [
        ("micro", 3 * 3600 * 1000000 + 4 * 60 * 1000000 + 5 * 1000000 + 600000),
        ("milli", 3 * 3600 * 1000 + 4 * 60 * 1000 + 5 * 1000 + 600),
        ("sec", 3 * 3600 + 4 * 60 + 5),
    ],
)
def test_u_token_precision(writer, freeze_time, precision, expected):
    original = _cfg.TIMESTAMP_PRECISION
    _cfg.TIMESTAMP_PRECISION = precision
    try:
        with freeze_time("2011-01-02 03:04:05.6", ("UTC", 0)):
            logger.add(writer, format="{time:u}")
            logger.debug("X")
            assert writer.read() == "%d\n" % expected
    finally:
        _cfg.TIMESTAMP_PRECISION = original


def test_u_token_does_not_break_existing_tokens(writer, freeze_time):
    original = _cfg.TIMESTAMP_PRECISION
    _cfg.TIMESTAMP_PRECISION = "sec"
    try:
        with freeze_time("2011-01-02 03:04:05.6", ("UTC", 0)):
            logger.add(writer, format="{time:YYYY-MM-DD HH:mm:ss} | {time:u}")
            logger.debug("X")
            assert writer.read() == "2011-01-02 03:04:05 | %d\n" % (3 * 3600 + 4 * 60 + 5)
    finally:
        _cfg.TIMESTAMP_PRECISION = original


def test_u_token_compile_direct():
    # Direct formatter call (no logger involved).
    original = _cfg.TIMESTAMP_PRECISION
    _cfg.TIMESTAMP_PRECISION = "sec"
    try:
        from loguru._datetime import datetime as ldt

        value = ldt(2011, 1, 2, 3, 4, 5, 600000)
        formatter = _compile_format("u")
        result = formatter(value)
        assert result == str(3 * 3600 + 4 * 60 + 5)
    finally:
        _cfg.TIMESTAMP_PRECISION = original
