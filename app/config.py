from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_PATH = Path("config.json")


@dataclass(frozen=True)
class AppConfig:
    reminder_interval_minutes: float = 25
    break_duration_seconds: int = 20
    pause_minutes: float = 60
    idle_threshold_minutes: float = 5


DEFAULT_CONFIG = AppConfig()


def load_config(path: Path = CONFIG_PATH) -> AppConfig:
    if not path.exists():
        save_config(DEFAULT_CONFIG, path)
        return DEFAULT_CONFIG

    try:
        raw_config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CONFIG

    if not isinstance(raw_config, dict):
        return DEFAULT_CONFIG

    return AppConfig(
        reminder_interval_minutes=_positive_number(
            raw_config.get("reminder_interval_minutes"),
            DEFAULT_CONFIG.reminder_interval_minutes,
        ),
        break_duration_seconds=int(
            _positive_number(
                raw_config.get("break_duration_seconds"),
                DEFAULT_CONFIG.break_duration_seconds,
            )
        ),
        pause_minutes=_positive_number(
            raw_config.get("pause_minutes"),
            DEFAULT_CONFIG.pause_minutes,
        ),
        idle_threshold_minutes=_non_negative_number(
            raw_config.get("idle_threshold_minutes"),
            DEFAULT_CONFIG.idle_threshold_minutes,
        ),
    )


def save_config(config: AppConfig, path: Path = CONFIG_PATH) -> None:
    payload = {
        "reminder_interval_minutes": config.reminder_interval_minutes,
        "break_duration_seconds": config.break_duration_seconds,
        "pause_minutes": config.pause_minutes,
        "idle_threshold_minutes": config.idle_threshold_minutes,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _positive_number(value: Any, fallback: float) -> float:
    if isinstance(value, bool):
        return fallback

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback

    if parsed <= 0:
        return fallback
    return parsed


def _non_negative_number(value: Any, fallback: float) -> float:
    if isinstance(value, bool):
        return fallback

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback

    if parsed < 0:
        return fallback
    return parsed
