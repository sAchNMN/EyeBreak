from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    left: int
    top: int
    right: int
    bottom: int


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

        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd or hwnd == ctypes.windll.user32.GetShellWindow():
            return False
        if not ctypes.windll.user32.IsWindowVisible(hwnd):
            return False

        window_rect = RECT()
        if not ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(window_rect)):
            return False

        monitor = ctypes.windll.user32.MonitorFromWindow(hwnd, 2)
        if not monitor:
            return False

        monitor_info = MONITORINFO()
        monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
        if not ctypes.windll.user32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info)):
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
