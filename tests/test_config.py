from pathlib import Path

from app.config import DEFAULT_CONFIG, AppConfig, load_config, save_config


def test_load_config_creates_default_when_missing(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"

    config = load_config(config_path)

    assert config == DEFAULT_CONFIG
    assert config_path.exists()


def test_load_config_reads_custom_values(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
        {
          "reminder_interval_minutes": 0.1,
          "break_duration_seconds": 10,
          "pause_minutes": 0.5,
          "idle_threshold_minutes": 3,
          "fullscreen_detection_enabled": false
        }
        """,
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config == AppConfig(
        reminder_interval_minutes=0.1,
        break_duration_seconds=10,
        pause_minutes=0.5,
        idle_threshold_minutes=3,
        fullscreen_detection_enabled=False,
    )


def test_load_config_uses_default_for_invalid_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{bad json", encoding="utf-8")

    config = load_config(config_path)

    assert config == DEFAULT_CONFIG


def test_load_config_allows_zero_idle_threshold_for_disabled(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
        {
          "reminder_interval_minutes": 10,
          "break_duration_seconds": 10,
          "pause_minutes": 5,
          "idle_threshold_minutes": 0
        }
        """,
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.idle_threshold_minutes == 0


def test_load_config_defaults_fullscreen_detection_when_missing(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
        {
          "reminder_interval_minutes": 10,
          "break_duration_seconds": 10,
          "pause_minutes": 5,
          "idle_threshold_minutes": 1
        }
        """,
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.fullscreen_detection_enabled is True


def test_save_config_writes_fullscreen_detection_flag(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"

    save_config(AppConfig(fullscreen_detection_enabled=False), config_path)

    config = load_config(config_path)
    assert config.fullscreen_detection_enabled is False
