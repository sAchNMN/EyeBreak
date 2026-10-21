from pathlib import Path

import math

import pytest

from app.config import (
    CONFIG_PATH,
    DEFAULT_CONFIG,
    AppConfig,
    ConfigValidationError,
    load_config,
    parse_config_values,
    save_config,
    validate_config,
)


def test_default_config_path_is_absolute() -> None:
    assert CONFIG_PATH.is_absolute()


def test_load_config_creates_default_when_missing(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"

    config = load_config(config_path)

    assert config == DEFAULT_CONFIG
    assert config_path.exists()


def test_load_config_uses_default_when_missing_file_cannot_be_created(monkeypatch) -> None:
    def raise_permission_error(config: AppConfig, path: Path) -> None:
        raise PermissionError

    monkeypatch.setattr("app.config.save_config", raise_permission_error)

    assert load_config(Path("missing-config.json")) == DEFAULT_CONFIG


def test_load_config_reads_custom_values(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
        {
          "reminder_interval_minutes": 0.1,
          "break_duration_seconds": 10,
          "pause_minutes": 1.5,
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
        pause_minutes=1.5,
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


@pytest.mark.parametrize(
    "field,value",
    [
        ("reminder_interval_minutes", 0),
        ("reminder_interval_minutes", 1441),
        ("break_duration_seconds", 0),
        ("break_duration_seconds", 3601),
        ("pause_minutes", 0),
        ("pause_minutes", 121),
        ("idle_threshold_minutes", -1),
        ("idle_threshold_minutes", 1441),
    ],
)
def test_validate_config_rejects_out_of_range_values(field: str, value) -> None:
    config = AppConfig(**{field: value})

    with pytest.raises(ConfigValidationError):
        validate_config(config)


@pytest.mark.parametrize(
    "field",
    [
        "reminder_interval_minutes",
        "break_duration_seconds",
        "pause_minutes",
        "idle_threshold_minutes",
    ],
)
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_validate_config_rejects_non_finite_values(field: str, value: float) -> None:
    config = AppConfig(**{field: value})

    with pytest.raises(ConfigValidationError):
        validate_config(config)


def test_load_config_uses_default_for_out_of_range_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '{"reminder_interval_minutes": 1441}', encoding="utf-8"
    )

    assert load_config(config_path) == DEFAULT_CONFIG


def test_parse_config_values_returns_config() -> None:
    config = parse_config_values("15", "20", "30", "0", False)

    assert config == AppConfig(
        reminder_interval_minutes=15,
        break_duration_seconds=20,
        pause_minutes=30,
        idle_threshold_minutes=0,
        fullscreen_detection_enabled=False,
    )


def test_parse_config_values_allows_decimal_minutes() -> None:
    config = parse_config_values("0.5", "10", "1.5", "2.5", True)

    assert config.reminder_interval_minutes == 0.5
    assert config.pause_minutes == 1.5
    assert config.idle_threshold_minutes == 2.5
    assert config.fullscreen_detection_enabled is True


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (("0", "20", "30", "5"), "提醒间隔必须大于 0"),
        (("15", "1.5", "30", "5"), "休息时长必须是大于 0 的整数"),
        (("15", "20", "0", "5"), "默认暂停必须大于 0"),
        (("15", "20", "30", "-1"), "离开检测不能小于 0"),
        (("1441", "20", "30", "5"), "提醒间隔必须是有限数值且大于 0、不能超过 1440 分钟"),
        (("15", "20", "121", "5"), "默认暂停必须是有限数值，范围为 1 到 120 分钟"),
        (("NaN", "20", "30", "5"), "提醒间隔必须是有限数值且大于 0、不能超过 1440 分钟"),
    ],
)
def test_parse_config_values_rejects_invalid_values(
    values: tuple[str, str, str, str],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        parse_config_values(*values)
