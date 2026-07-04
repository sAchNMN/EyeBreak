from pathlib import Path
from unittest.mock import patch

from app.paths import app_base_dir, runtime_file_path


def test_app_base_dir_uses_project_root_in_source_mode() -> None:
    assert app_base_dir() == Path(__file__).resolve().parent.parent


def test_app_base_dir_uses_exe_folder_when_frozen() -> None:
    with patch("app.paths.sys") as mock_sys:
        mock_sys.frozen = True
        mock_sys.executable = r"C:\Apps\EyeBreak\EyeBreak.exe"

        assert app_base_dir() == Path(r"C:\Apps\EyeBreak")


def test_runtime_file_path_uses_app_base_dir() -> None:
    assert runtime_file_path("config.json") == app_base_dir() / "config.json"
