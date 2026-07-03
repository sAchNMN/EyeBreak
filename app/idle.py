from __future__ import annotations

import sys


_IDLE_ZERO_FALLBACK = 0.0


def get_idle_seconds() -> float:
    """Return seconds since the last user input (keyboard/mouse).

    Uses GetLastInputInfo on Windows. Returns 0.0 on non-Windows or failure.
    """
    if sys.platform != "win32":
        return _IDLE_ZERO_FALLBACK

    try:
        import ctypes
        from ctypes import wintypes

        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("dwTime", wintypes.DWORD),
            ]

        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            return _IDLE_ZERO_FALLBACK

        return (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0
    except (AttributeError, OSError, TypeError):
        return _IDLE_ZERO_FALLBACK