from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable
from ctypes import wintypes
from functools import partial

import pystray

from app.icons import create_icon_image
from app.reminder_window import format_pause_label


PAUSE_OPTIONS_MINUTES = (5, 15, 30, 60, 120)

_LAST_NOTIFY_ADD: tuple[int, int] | None = None
_WINDOWS_PATCH_INSTALLED = False


def _install_windows_tray_compatibility_patch() -> None:
    """Keep pystray alive when Windows blocks its optional message filter.

    pystray 0.19.5 calls ``ChangeWindowMessageFilterEx`` while creating its
    hidden tray window.  Windows returns ``ERROR_ACCESS_DENIED`` for processes
    that are not running at the shell's integrity level (for example, an
    elevated process, or a process launched from a restricted terminal).  The
    exception kills pystray's tray thread, so the icon never appears.

    The call only opts the window into ``WM_TASKBARCREATED`` (explorer restart
    handling).  Losing that message is harmless, so treat the failure as a
    no-op instead of losing the whole tray icon.
    """
    global _WINDOWS_PATCH_INSTALLED
    if _WINDOWS_PATCH_INSTALLED or sys.platform != "win32":
        return

    try:
        from pystray._util import win32
    except (ImportError, AttributeError):
        return

    try:
        original_filter = win32.ChangeWindowMessageFilterEx
    except AttributeError:
        return

    def safe_change_window_message_filter_ex(*args, **kwargs):
        try:
            return original_filter(*args, **kwargs)
        except OSError:
            return 0

    win32.ChangeWindowMessageFilterEx = safe_change_window_message_filter_ex

    try:
        shell32 = ctypes.WinDLL("shell32", use_last_error=True)
        shell32.Shell_NotifyIconW.argtypes = (
            wintypes.DWORD,
            ctypes.POINTER(win32.NOTIFYICONDATAW),
        )
        shell32.Shell_NotifyIconW.restype = wintypes.BOOL
    except (AttributeError, OSError):
        _WINDOWS_PATCH_INSTALLED = True
        return

    def tracking_shell_notify_icon(code, data):
        global _LAST_NOTIFY_ADD
        result = shell32.Shell_NotifyIconW(code, ctypes.byref(data))
        if code == win32.NIM_ADD:
            _LAST_NOTIFY_ADD = (int(result), ctypes.get_last_error())
        return result

    win32.Shell_NotifyIcon = tracking_shell_notify_icon
    _WINDOWS_PATCH_INSTALLED = True


class TrayIcon:
    def __init__(
        self,
        on_break_now: Callable[[], None],
        on_pause: Callable[[int], None],
        on_resume: Callable[[], None],
        on_pause_today: Callable[[], None],
        on_open_settings: Callable[[], None],
        on_toggle_floating: Callable[[], None],
        get_is_floating_enabled: Callable[[], bool],
        on_toggle_autostart: Callable[[], None],
        get_is_autostart_enabled: Callable[[], bool],
        on_exit: Callable[[], None],
    ) -> None:
        _install_windows_tray_compatibility_patch()
        self.icon = pystray.Icon(
            "EyeBreak",
            create_icon_image(),
            "EyeBreak",
            pystray.Menu(
                pystray.MenuItem("立即休息", _action(on_break_now)),
                pystray.MenuItem("暂停", _pause_menu(on_pause)),
                pystray.MenuItem("恢复", _action(on_resume)),
                pystray.MenuItem("今天不再提醒", _action(on_pause_today)),
                pystray.MenuItem("设置", _action(on_open_settings)),
                pystray.MenuItem(
                    "开关悬浮窗",
                    _action(on_toggle_floating),
                    checked=lambda item: get_is_floating_enabled(),
                ),
                pystray.MenuItem(
                    "开机自启",
                    _action(on_toggle_autostart),
                    checked=lambda item: get_is_autostart_enabled(),
                ),
                pystray.MenuItem("退出", _action(on_exit)),
            ),
        )

    def start(self) -> None:
        self.icon.run_detached()

    def last_notify_result(self) -> tuple[int, int] | None:
        """Return ``(Shell_NotifyIcon result, GetLastError)`` for NIM_ADD."""
        return _LAST_NOTIFY_ADD

    def stop(self) -> None:
        self.icon.stop()

    def update_menu(self) -> None:
        """Force the menu to rebuild, re-evaluating all `checked` callbacks."""
        self.icon.update_menu()


def _pause_menu(on_pause: Callable[[int], None]) -> pystray.Menu:
    return pystray.Menu(
        *(
            pystray.MenuItem(
                format_pause_label(minutes),
                _action(partial(on_pause, minutes)),
            )
            for minutes in PAUSE_OPTIONS_MINUTES
        )
    )


def _action(
    callback: Callable[[], None],
) -> Callable[[pystray.Icon, pystray.MenuItem], None]:
    def action(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        callback()

    return action
