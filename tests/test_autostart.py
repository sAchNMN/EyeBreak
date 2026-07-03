from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from app.autostart import is_autostart_enabled, set_autostart


class TestSetAutostart:
    def test_enable_writes_to_run_key(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            mock_key = mock_winreg.OpenKey.return_value
            mock_winreg.__enter__ = mock_winreg  # trick to allow with-statement

            set_autostart(True)

            mock_winreg.OpenKey.assert_called_once()
            mock_winreg.SetValueEx.assert_called_once()
            # First arg to SetValueEx: key, name, reserved, type, value
            args, _ = mock_winreg.SetValueEx.call_args
            assert args[1] == "EyeBreak"
            assert args[3] == mock_winreg.REG_SZ
            assert isinstance(args[4], str)
            # The value should contain either pythonw.exe or sys.executable
            assert len(args[4]) > 0

    def test_disable_deletes_from_run_key(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            set_autostart(False)

            mock_winreg.DeleteValue.assert_called_once_with(
                mock_winreg.OpenKey.return_value, "EyeBreak"
            )

    def test_disable_ignores_file_not_found(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            mock_winreg.DeleteValue.side_effect = FileNotFoundError

            set_autostart(False)  # should not raise

            mock_winreg.DeleteValue.assert_called_once()


class TestIsAutostartEnabled:
    def test_returns_true_when_key_exists(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            # QueryValueEx returns (value, type) on success
            mock_winreg.QueryValueEx.return_value = ("some_path", 1)

            result = is_autostart_enabled()

            assert result is True

    def test_returns_false_when_key_missing(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            mock_winreg.QueryValueEx.side_effect = FileNotFoundError

            result = is_autostart_enabled()

            assert result is False

    def test_returns_false_on_os_error(self) -> None:
        with patch("app.autostart.winreg") as mock_winreg:
            mock_winreg.OpenKey.side_effect = OSError

            result = is_autostart_enabled()

            assert result is False


class TestGetTargetCommandSource:
    def test_includes_pythonw_when_available(self) -> None:
        """In normal source mode, the command includes pythonw.exe."""
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
