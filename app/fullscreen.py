from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Rect:
    left: int
    top: int
    right: int
    bottom: int


@lru_cache(maxsize=1)
def _get_win32_api():
    import ctypes
    from ctypes import wintypes

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", wintypes.LONG),
            ("top", wintypes.LONG),
            ("right", wintypes.LONG),
            ("bottom", wintypes.LONG),
        ]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", RECT),
            ("rcWork", RECT),
            ("dwFlags", wintypes.DWORD),
        ]

    user32 = ctypes.windll.user32
    return (
        user32.GetForegroundWindow,
        user32.GetShellWindow,
        user32.IsWindowVisible,
        user32.GetWindowRect,
        user32.MonitorFromWindow,
        user32.GetMonitorInfoW,
        RECT,
        MONITORINFO,
    )


def window_covers_monitor(
    window_rect: Rect,
    monitor_rect: Rect,
    tolerance: int = 2,
) -> bool:
    return (
        abs(window_rect.left - monitor_rect.left) <= tolerance
        and abs(window_rect.top - monitor_rect.top) <= tolerance
        and abs(window_rect.right - monitor_rect.right) <= tolerance
        and abs(window_rect.bottom - monitor_rect.bottom) <= tolerance
    )


def is_foreground_window_fullscreen() -> bool:
    if sys.platform != "win32":
        return False

    try:
        import ctypes
        (
            get_foreground_window,
            get_shell_window,
            is_window_visible,
            get_window_rect,
            monitor_from_window,
            get_monitor_info,
            rect_type,
            monitor_info_type,
        ) = _get_win32_api()

        hwnd = get_foreground_window()
        if not hwnd or hwnd == get_shell_window():
            return False
        if not is_window_visible(hwnd):
            return False

        window_rect = rect_type()
        if not get_window_rect(hwnd, ctypes.byref(window_rect)):
            return False

        monitor = monitor_from_window(hwnd, 2)
        if not monitor:
            return False

        monitor_info = monitor_info_type()
        monitor_info.cbSize = ctypes.sizeof(monitor_info_type)
        if not get_monitor_info(monitor, ctypes.byref(monitor_info)):
            return False

        return window_covers_monitor(
            Rect(
                window_rect.left,
                window_rect.top,
                window_rect.right,
                window_rect.bottom,
            ),
            Rect(
                monitor_info.rcMonitor.left,
                monitor_info.rcMonitor.top,
                monitor_info.rcMonitor.right,
                monitor_info.rcMonitor.bottom,
            ),
        )
    except (AttributeError, OSError, TypeError, ValueError):
        return False
