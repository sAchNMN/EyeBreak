from __future__ import annotations

import sys
import winreg
from pathlib import Path


APP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_APPROVED_KEY = (
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
)
APP_NAME = "EyeBreak"
STARTUP_ENABLED_VALUE = b"\x02" + b"\x00" * 11


def _get_target_command() -> str:
    """Return the command that should be registered for autostart."""
    if getattr(sys, "frozen", False) and hasattr(sys, "executable"):
        return f'"{Path(sys.executable).resolve()}"'

    script_path = Path(sys.argv[0]).resolve()
    interpreter = Path(sys.executable).resolve()
    pythonw = interpreter.with_name("pythonw.exe")
    if pythonw.is_file():
        return f'"{pythonw}" "{script_path}"'
    return f'"{interpreter}" "{script_path}"'


def set_autostart(enabled: bool) -> None:
    """Synchronize Run and StartupApproved entries for EyeBreak."""
    key = winreg.CreateKeyEx(
        winreg.HKEY_CURRENT_USER, APP_KEY, 0, winreg.KEY_SET_VALUE
    )
    try:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _get_target_command())
            _set_startup_approved(True)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
            _set_startup_approved(False)
    finally:
        winreg.CloseKey(key)


def is_autostart_enabled() -> bool:
    """Check both the Run entry and Windows StartupApproved status."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, APP_KEY, 0, winreg.KEY_QUERY_VALUE
        )
        try:
            command, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(command) and _is_startup_approved()
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except OSError:
        return False


def _set_startup_approved(enabled: bool) -> None:
    key = winreg.CreateKeyEx(
        winreg.HKEY_CURRENT_USER, STARTUP_APPROVED_KEY, 0, winreg.KEY_SET_VALUE
    )
    try:
        if enabled:
            winreg.SetValueEx(
                key, APP_NAME, 0, winreg.REG_BINARY, STARTUP_ENABLED_VALUE
            )
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
    finally:
        winreg.CloseKey(key)


def _is_startup_approved() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            STARTUP_APPROVED_KEY,
            0,
            winreg.KEY_QUERY_VALUE,
        )
        try:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
        except FileNotFoundError:
            return True
        finally:
            winreg.CloseKey(key)
    except OSError:
        return True

    return not isinstance(value, bytes) or not value or value[0] != 0x03