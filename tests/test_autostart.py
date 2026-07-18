from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import ANY, call, patch

from app.autostart import (
    APP_KEY,
    APP_NAME,
    STARTUP_APPROVED_KEY,
    STARTUP_ENABLED_VALUE,
    is_autostart_enabled,
    set_autostart,
)


class TestSetAutostart:
    def test_enable_writes_run_and_startup_approved_entries(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            run_key = object()
            approved_key = object()
            mock_winreg.CreateKeyEx.side_effect = [run_key, approved_key]

            set_autostart(True)

            assert mock_winreg.CreateKeyEx.call_args_list == [
                call(mock_winreg.HKEY_CURRENT_USER, APP_KEY, 0, mock_winreg.KEY_SET_VALUE),
                call(
                    mock_winreg.HKEY_CURRENT_USER,
                    STARTUP_APPROVED_KEY,
                    0,
                    mock_winreg.KEY_SET_VALUE,
                ),
            ]
            assert mock_winreg.SetValueEx.call_args_list == [
                call(run_key, APP_NAME, 0, mock_winreg.REG_SZ, ANY),
                call(
                    approved_key,
                    APP_NAME,
                    0,
                    mock_winreg.REG_BINARY,
                    STARTUP_ENABLED_VALUE,
                ),
            ]
            assert mock_winreg.CloseKey.call_args_list == [
                call(approved_key),
                call(run_key),
            ]

    def test_disable_removes_run_and_startup_approved_entries(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            run_key = object()
            approved_key = object()
            mock_winreg.CreateKeyEx.side_effect = [run_key, approved_key]

            set_autostart(False)

            assert mock_winreg.DeleteValue.call_args_list == [
                call(run_key, APP_NAME),
                call(approved_key, APP_NAME),
            ]

    def test_disable_ignores_missing_entries(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            mock_winreg.DeleteValue.side_effect = [FileNotFoundError, FileNotFoundError]

            set_autostart(False)

            assert mock_winreg.DeleteValue.call_count == 2


class TestIsAutostartEnabled:
    def test_returns_true_when_run_and_approval_entries_are_enabled(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            mock_winreg.OpenKey.side_effect = [object(), object()]
            mock_winreg.QueryValueEx.side_effect = [
                ("some_path", 1),
                (STARTUP_ENABLED_VALUE, 1),
            ]

            assert is_autostart_enabled() is True

    def test_returns_false_when_startup_approved_is_disabled(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            mock_winreg.OpenKey.side_effect = [object(), object()]
            mock_winreg.QueryValueEx.side_effect = [("some_path", 1), (b"\x03", 1)]

            assert is_autostart_enabled() is False

    def test_returns_false_when_run_entry_is_missing(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            mock_winreg.QueryValueEx.side_effect = FileNotFoundError

            assert is_autostart_enabled() is False


class TestGetTargetCommandSource:
    def test_includes_pythonw_when_available(self) -> None:
        with (
            patch("app.autostart.sys") as mock_sys,
            patch("app.autostart.Path.is_file") as mock_is_file,
        ):
            mock_sys.argv = ["main.py"]
            mock_sys.executable = r"C:\Python\python.exe"
            mock_is_file.return_value = True
            mock_sys.frozen = False

            from app.autostart import _get_target_command

            cmd = _get_target_command()
            assert "pythonw.exe" in cmd
            assert "main.py" in cmd

    def test_falls_back_to_python_when_pythonw_missing(self) -> None:
        with (
            patch("app.autostart.sys") as mock_sys,
            patch("app.autostart.Path.is_file") as mock_is_file,
        ):
            mock_sys.argv = ["main.py"]
            mock_sys.executable = r"C:\Python\python.exe"
            mock_is_file.return_value = False
            mock_sys.frozen = False

            from app.autostart import _get_target_command

            cmd = _get_target_command()
            assert "python.exe" in cmd
            assert "main.py" in cmd

    def test_uses_exe_path_when_frozen(self) -> None:
        with (
            patch("app.autostart.sys") as mock_sys,
            patch("app.autostart.Path.is_file") as mock_is_file,
        ):
            mock_sys.argv = ["main.py"]
            mock_sys.executable = r"C:\dist\EyeBreak\EyeBreak.exe"
            mock_sys.frozen = True

            from app.autostart import _get_target_command

            cmd = _get_target_command()
            assert "EyeBreak.exe" in cmd
            assert "python" not in cmd