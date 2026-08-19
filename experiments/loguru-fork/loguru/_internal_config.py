"""Fork-specific internal configuration.

This module is NOT part of upstream loguru. It centralizes build-time
tuning knobs that operators may flip when deploying this fork.

``TIMESTAMP_PRECISION`` controls the number of fractional-second digits
used by the legacy "x" token when rendering UNIX timestamps:

    - "micro"  (default): 6 fractional digits, e.g. "1771716252000001"
    - "milli"  : 3 fractional digits, e.g. "1771716252000"
    - "sec"    : 0 fractional digits, e.g. "1771716252"

Other modules read this value lazily at render time, so flipping it does
not require recompiling or restarting a long-lived process.
"""

TIMESTAMP_PRECISION = "micro"
