from pathlib import Path

from app.config import DEFAULT_CONFIG, AppConfig, load_config


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
          "pause_minutes": 0.5
        }
        """,
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config == AppConfig(
        reminder_interval_minutes=0.1,
        break_duration_seconds=10,
        pause_minutes=0.5,
    )


def test_load_config_uses_default_for_invalid_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{bad json", encoding="utf-8")

    config = load_config(config_path)

    assert config == DEFAULT_CONFIG
