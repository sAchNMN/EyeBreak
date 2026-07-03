import sys
from unittest.mock import patch

from app.idle import get_idle_seconds


def test_get_idle_seconds_non_windows_returns_zero() -> None:
    with patch.object(sys, "platform", "darwin"):
        result = get_idle_seconds()

    assert result == 0.0


def test_get_idle_seconds_windows_calls_api() -> None:
    if sys.platform != "win32":
        return  # skip on non-Windows; no API available

    result = get_idle_seconds()

    # On a real Windows system, this returns >= 0 (time since last input)
    assert result >= 0