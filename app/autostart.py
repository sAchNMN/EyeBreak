from __future__ import annotations

import sys
import winreg
from pathlib import Path

APP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "EyeBreak"


def _get_target_command() -> str:
    """Return the command that should be registered for autostart.

    When running from a PyInstaller-built executable, use the exe path
    directly. When running from source, use "pythonw.exe main.py" to
    avoid a visible console window.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "executable"):
        return f'"{Path(sys.executable).resolve()}"'

    # Running from source — resolve the script path
    script_path = Path(sys.argv[0]).resolve()

    # Use pythonw.exe alongside python.exe to suppress the console
    interpreter = Path(sys.executable).resolve()
    pythonw = interpreter.with_name("pythonw.exe")
    if pythonw.is_file():
        return f'"{pythonw}" "{script_path}"'
    return f'"{interpreter}" "{script_path}"'


def set_autostart(enabled: bool) -> None:
    """Enable or disable the EyeBreak autostart entry in HKCU\\...\\Run."""
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, APP_KEY, 0, winreg.KEY_SET_VALUE
    )
    try:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _get_target_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
    finally:
        winreg.CloseKey(key)


def is_autostart_enabled() -> bool:
    """Check whether EyeBreak is registered in HKCU\\...\\Run."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, APP_KEY, 0, winreg.KEY_QUERY_VALUE
        )
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except OSError:
        return False
