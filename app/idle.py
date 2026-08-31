from __future__ import annotations

import sys
from functools import lru_cache


_IDLE_ZERO_FALLBACK = 0.0


@lru_cache(maxsize=1)
def _get_win32_api():
    import ctypes
    from ctypes import wintypes

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("dwTime", wintypes.DWORD),
        ]

    return (
        ctypes.windll.user32.GetLastInputInfo,
        ctypes.windll.kernel32.GetTickCount,
        LASTINPUTINFO,
    )


def get_idle_seconds() -> float:
    """Return seconds since the last user input (keyboard/mouse).

    Uses GetLastInputInfo on Windows. Returns 0.0 on non-Windows or failure.
    """
    if sys.platform != "win32":
        return _IDLE_ZERO_FALLBACK

    try:
        get_last_input_info, get_tick_count, last_input_info_type = _get_win32_api()
        import ctypes

        lii = last_input_info_type()
        lii.cbSize = ctypes.sizeof(last_input_info_type)
        if not get_last_input_info(ctypes.byref(lii)):
            return _IDLE_ZERO_FALLBACK

        return (get_tick_count() - lii.dwTime) / 1000.0
    except (AttributeError, OSError, TypeError):
        return _IDLE_ZERO_FALLBACK
