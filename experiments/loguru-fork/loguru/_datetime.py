"""Time format rendering for the fork.

Differs from upstream loguru: tokens are registered via a registry
("register_time_token") instead of a flat literal dict. Behavior is
otherwise identical.
"""

import re
from calendar import day_abbr, day_name, month_abbr, month_name
from datetime import datetime as datetime_
from datetime import timedelta, timezone
from functools import lru_cache, partial
from time import localtime, strftime

from . import _internal_config

tokens = r"H{1,2}|h{1,2}|m{1,2}|s{1,2}|S+|YYYY|YY|M{1,4}|D{1,4}|Z{1,2}|zz|A|X|x|u|E|Q|dddd|ddd|d"

pattern = re.compile(r"(?:{0})|\[(?:{0}|!UTC|)\]".format(tokens))

# --- Token registry (replaces the upstream flat dict) -----------------------
_TIME_TOKEN_REGISTRY = {}


def register_time_token(name, specifier, formatter):
    """Register a time format token usable inside ``{time:...}``."""
    if name in _TIME_TOKEN_REGISTRY:
        raise ValueError("Time token already registered: %r" % name)
    _TIME_TOKEN_REGISTRY[name] = (specifier, formatter)


def _register_default_tokens():
    register_time_token("YYYY", "%04d", lambda t, dt: t.tm_year)
    register_time_token("YY", "%02d", lambda t, dt: t.tm_year % 100)
    register_time_token("Q", "%d", lambda t, dt: (t.tm_mon - 1) // 3 + 1)
    register_time_token("MMMM", "%s", lambda t, dt: month_name[t.tm_mon])
    register_time_token("MMM", "%s", lambda t, dt: month_abbr[t.tm_mon])
    register_time_token("MM", "%02d", lambda t, dt: t.tm_mon)
    register_time_token("M", "%d", lambda t, dt: t.tm_mon)
    register_time_token("DDDD", "%03d", lambda t, dt: t.tm_yday)
    register_time_token("DDD", "%d", lambda t, dt: t.tm_yday)
    register_time_token("DD", "%02d", lambda t, dt: t.tm_mday)
    register_time_token("D", "%d", lambda t, dt: t.tm_mday)
    register_time_token("dddd", "%s", lambda t, dt: day_name[t.tm_wday])
    register_time_token("ddd", "%s", lambda t, dt: day_abbr[t.tm_wday])
    register_time_token("d", "%d", lambda t, dt: t.tm_wday)
    register_time_token("E", "%d", lambda t, dt: t.tm_wday + 1)
    register_time_token("HH", "%02d", lambda t, dt: t.tm_hour)
    register_time_token("H", "%d", lambda t, dt: t.tm_hour)
    register_time_token("hh", "%02d", lambda t, dt: (t.tm_hour - 1) % 12 + 1)
    register_time_token("h", "%d", lambda t, dt: (t.tm_hour - 1) % 12 + 1)
    register_time_token("mm", "%02d", lambda t, dt: t.tm_min)
    register_time_token("m", "%d", lambda t, dt: t.tm_min)
    register_time_token("ss", "%02d", lambda t, dt: t.tm_sec)
    register_time_token("s", "%d", lambda t, dt: t.tm_sec)
    register_time_token("S", "%d", lambda t, dt: dt.microsecond // 100000)
    register_time_token("SS", "%02d", lambda t, dt: dt.microsecond // 10000)
    register_time_token("SSS", "%03d", lambda t, dt: dt.microsecond // 1000)
    register_time_token("SSSS", "%04d", lambda t, dt: dt.microsecond // 100)
    register_time_token("SSSSS", "%05d", lambda t, dt: dt.microsecond // 10)
    register_time_token("SSSSSS", "%06d", lambda t, dt: dt.microsecond)
    register_time_token("A", "%s", lambda t, dt: "AM" if t.tm_hour < 12 else "PM")
    register_time_token("Z", "%s", lambda t, dt: _format_timezone(dt, sep=":"))
    register_time_token("ZZ", "%s", lambda t, dt: _format_timezone(dt, sep=""))
    register_time_token("zz", "%s", lambda t, dt: (dt.tzinfo or timezone.utc).tzname(dt) or "")
    register_time_token("X", "%d", lambda t, dt: dt.timestamp())
    def _unix_epoch_micros(dt):
        # Precise integer math: avoids float rounding drift in dt.timestamp().
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        epoch = datetime_(1970, 1, 1, tzinfo=timezone.utc)
        delta = dt - epoch
        total_micros = (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
        if _internal_config.TIMESTAMP_PRECISION == "milli":
            return total_micros // 1000
        if _internal_config.TIMESTAMP_PRECISION == "sec":
            return total_micros // 1000000
        return total_micros

    register_time_token("x", "%d", lambda t, dt: _unix_epoch_micros(dt))

    def _seconds_since_midnight(dt):
        # Seconds elapsed since local midnight, with fractional precision
        # controlled by TIMESTAMP_PRECISION (same pattern as the x token).
        total = (dt.hour * 3600 + dt.minute * 60 + dt.second) * 1000000 + dt.microsecond
        if _internal_config.TIMESTAMP_PRECISION == "milli":
            return total // 1000
        if _internal_config.TIMESTAMP_PRECISION == "sec":
            return total // 1000000
        return total

    register_time_token("u", "%d", lambda t, dt: _seconds_since_midnight(dt))


_register_default_tokens()


def _builtin_datetime_formatter(is_utc, format_string, dt):
    if is_utc:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime(format_string)


def _loguru_datetime_formatter(is_utc, format_string, formatters, dt):
    if is_utc:
        dt = dt.astimezone(timezone.utc)
    t = dt.timetuple()
    args = tuple(f(t, dt) for f in formatters)
    return format_string % args


def _default_datetime_formatter(dt):
    return "%04d-%02d-%02d %02d:%02d:%02d.%03d %s" % (
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond // 1000,
        _format_timezone(dt, sep=":"),
    )


def _format_timezone(dt, *, sep):
    tzinfo = dt.tzinfo or timezone.utc
    offset = tzinfo.utcoffset(dt).total_seconds()
    sign = "+" if offset >= 0 else "-"
    (h, m), s = divmod(abs(offset // 60), 60), abs(offset) % 60
    z = "%s%02d%s%02d" % (sign, h, sep, m)
    if s > 0:
        if s.is_integer():
            z += "%s%02d" % (sep, s)
        else:
            z += "%s%09.06f" % (sep, s)
    return z


@lru_cache(maxsize=32)
def _compile_format(spec):
    if spec == "YYYY-MM-DD HH:mm:ss.SSS Z":
        return _default_datetime_formatter

    is_utc = spec.endswith("!UTC")

    if is_utc:
        spec = spec[:-4]

    if not spec:
        spec = "%Y-%m-%dT%H:%M:%S.%f%z"

    if "%" in spec:
        return partial(_builtin_datetime_formatter, is_utc, spec)

    if "SSSSSSS" in spec:
        raise ValueError(
            "Invalid time format: the provided format string contains more than six successive "
            "'S' characters. This may be due to an attempt to use nanosecond precision, which "
            "is not supported."
        )

    format_string = ""
    formatters = []
    pos = 0

    for match in pattern.finditer(spec):
        start, end = match.span()
        format_string += spec[pos:start]
        pos = end

        token = match.group(0)

        try:
            specifier, formatter = _TIME_TOKEN_REGISTRY[token]
        except KeyError:
            format_string += token[1:-1]
        else:
            format_string += specifier
            formatters.append(formatter)

    format_string += spec[pos:]

    return partial(_loguru_datetime_formatter, is_utc, format_string, formatters)


class datetime(datetime_):  # noqa: N801
    def __format__(self, fmt):
        return _compile_format(fmt)(self)


def _fallback_tzinfo(timestamp):
    utc_naive = datetime_.fromtimestamp(timestamp, tz=timezone.utc).replace(tzinfo=None)
    offset = datetime_.fromtimestamp(timestamp) - utc_naive
    seconds = offset.total_seconds()
    zone = strftime("%Z")
    return timezone(timedelta(seconds=seconds), zone)


def _get_tzinfo(timestamp):
    try:
        local = localtime(timestamp)
    except (OSError, OverflowError):
        # The "localtime()" can overflow on some platforms when the timestamp is too large.
        # Not sure the fallback won't also overflow, though.
        return _fallback_tzinfo(timestamp)

    try:
        seconds = local.tm_gmtoff
        zone = local.tm_zone
    except AttributeError:
        # The attributes were not availanble on all platforms before Python 3.6.
        return _fallback_tzinfo(timestamp)

    try:
        return timezone(timedelta(seconds=seconds), zone)
    except ValueError:
        # The number of seconds returned by "tm_gmtoff" might be invalid on Windows (year 2038+).
        # Curiously, the fallback workaround does not exhibit the same problem.
        return _fallback_tzinfo(timestamp)


def aware_now():
    now = datetime_.now()
    timestamp = now.timestamp()
    tzinfo = _get_tzinfo(timestamp)
    return datetime.combine(now.date(), now.time().replace(tzinfo=tzinfo))
