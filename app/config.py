from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.paths import runtime_file_path
from app.persistence import atomic_write_json, read_json_object


CONFIG_PATH = runtime_file_path("config.json")


@dataclass(frozen=True)
class AppConfig:
    reminder_interval_minutes: float = 25
    break_duration_seconds: int = 20
    pause_minutes: float = 60
    idle_threshold_minutes: float = 5
    fullscreen_detection_enabled: bool = True


DEFAULT_CONFIG = AppConfig()


class ConfigValidationError(ValueError):
    """Raised when a configuration value is outside its supported range."""


def load_config(path: Path = CONFIG_PATH) -> AppConfig:
    if not path.exists():
        try:
            save_config(DEFAULT_CONFIG, path)
        except OSError:
            return DEFAULT_CONFIG
        return DEFAULT_CONFIG

    raw_config = read_json_object(path, {}, backup=True)
    if not raw_config:
        return DEFAULT_CONFIG

    config = AppConfig(
        reminder_interval_minutes=_positive_number(
            raw_config.get("reminder_interval_minutes"),
            DEFAULT_CONFIG.reminder_interval_minutes,
        ),
        break_duration_seconds=_integer_number(
            raw_config.get("break_duration_seconds"),
            DEFAULT_CONFIG.break_duration_seconds,
        ),
        pause_minutes=_positive_number(
            raw_config.get("pause_minutes"),
            DEFAULT_CONFIG.pause_minutes,
        ),
        idle_threshold_minutes=_non_negative_number(
            raw_config.get("idle_threshold_minutes"),
            DEFAULT_CONFIG.idle_threshold_minutes,
        ),
        fullscreen_detection_enabled=_bool_value(
            raw_config.get("fullscreen_detection_enabled"),
            DEFAULT_CONFIG.fullscreen_detection_enabled,
        ),
    )
    try:
        return validate_config(config)
    except ConfigValidationError:
        return DEFAULT_CONFIG


def save_config(config: AppConfig, path: Path = CONFIG_PATH) -> None:
    config = validate_config(config)
    payload = {
        "reminder_interval_minutes": config.reminder_interval_minutes,
        "break_duration_seconds": config.break_duration_seconds,
        "pause_minutes": config.pause_minutes,
        "idle_threshold_minutes": config.idle_threshold_minutes,
        "fullscreen_detection_enabled": config.fullscreen_detection_enabled,
    }
    atomic_write_json(path, payload, backup=True)


def validate_config(config: AppConfig) -> AppConfig:
    """Validate and return a configuration before it enters the application."""
    _validate_number(
        config.reminder_interval_minutes,
        "提醒间隔必须是有限数值且大于 0、不能超过 1440 分钟",
        minimum=0,
        maximum=1440,
        minimum_inclusive=False,
    )
    if (
        isinstance(config.break_duration_seconds, bool)
        or not isinstance(config.break_duration_seconds, int)
    ):
        raise ConfigValidationError("休息时长必须是大于 0 且不超过 3600 的整数")
    _validate_number(
        config.break_duration_seconds,
        "休息时长必须是大于 0 且不超过 3600 的整数",
        minimum=1,
        maximum=3600,
        minimum_inclusive=True,
    )
    _validate_number(
        config.pause_minutes,
        "默认暂停必须是有限数值，范围为 1 到 120 分钟",
        minimum=1,
        maximum=120,
        minimum_inclusive=True,
    )
    _validate_number(
        config.idle_threshold_minutes,
        "离开检测必须是有限数值，范围为 0 到 1440 分钟",
        minimum=0,
        maximum=1440,
        minimum_inclusive=True,
    )
    if not isinstance(config.fullscreen_detection_enabled, bool):
        raise ConfigValidationError("全屏检测开关必须是布尔值")
    return config


def _validate_number(
    value: Any,
    message: str,
    *,
    minimum: float,
    maximum: float,
    minimum_inclusive: bool,
) -> None:
    if isinstance(value, bool):
        raise ConfigValidationError(message)
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ConfigValidationError(message) from exc
    minimum_failed = parsed < minimum or (
        not minimum_inclusive and parsed <= minimum
    )
    if not math.isfinite(parsed) or minimum_failed or parsed > maximum:
        raise ConfigValidationError(message)


def _positive_number(value: Any, fallback: float) -> float:
    if isinstance(value, bool):
        return fallback

    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return fallback

    if not math.isfinite(parsed) or parsed <= 0:
        return fallback
    return parsed


def _integer_number(value: Any, fallback: int) -> int:
    if isinstance(value, bool):
        return fallback
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return fallback
    if not math.isfinite(parsed) or not parsed.is_integer() or parsed <= 0:
        return fallback
    return int(parsed)


def _non_negative_number(value: Any, fallback: float) -> float:
    if isinstance(value, bool):
        return fallback

    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return fallback

    if not math.isfinite(parsed) or parsed < 0:
        return fallback
    return parsed


def _bool_value(value: Any, fallback: bool) -> bool:
    if isinstance(value, bool):
        return value
    return fallback
