from __future__ import annotations

import logging
from datetime import date
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.paths import runtime_file_path
from app.persistence import atomic_write_json, read_json_object


APP_STATE_PATH = runtime_file_path("app_state.json")
VALID_FLOATING_EDGES = {"left", "right", "top", "bottom"}
logger = logging.getLogger(__name__)


@dataclass
class AppState:
    is_running: bool = True
    paused_until: float = 0.0
    next_reminder_at: float = 0.0
    floating_countdown_enabled: bool = True
    floating_countdown_edge: str | None = "right"
    floating_countdown_x: int = 0
    floating_countdown_y: int | None = None
    today_pause_date: str | None = None


def load_app_state(path: Path = APP_STATE_PATH) -> AppState:
    if not path.exists():
        return AppState()

    raw_state = read_json_object(path, {})
    if not raw_state:
        return AppState()

    floating_state = raw_state.get("floating_countdown")
    if not isinstance(floating_state, dict):
        floating_state = {}

    return AppState(
        floating_countdown_enabled=_bool_value(
            floating_state.get("enabled"), True
        ),
        floating_countdown_edge=_floating_edge(floating_state.get("edge")),
        floating_countdown_x=_int_value(floating_state.get("x"), 0),
        floating_countdown_y=_optional_int_value(floating_state.get("y")),
        today_pause_date=_date_value(raw_state.get("today_pause_date")),
    )


def save_app_state(state: AppState, path: Path = APP_STATE_PATH) -> None:
    payload = {
        "floating_countdown": {
            "enabled": state.floating_countdown_enabled,
            "edge": state.floating_countdown_edge,
            "x": state.floating_countdown_x,
            "y": state.floating_countdown_y,
        }
    }
    today_pause_date = _date_value(state.today_pause_date)
    if today_pause_date is not None:
        payload["today_pause_date"] = today_pause_date
    try:
        atomic_write_json(path, payload)
    except OSError:
        logger.exception("Could not save application state to %s", path)


def _floating_edge(value: Any) -> str | None:
    if value in VALID_FLOATING_EDGES:
        return str(value)
    if value is None:
        return None
    return "right"


def _bool_value(value: Any, fallback: bool) -> bool:
    return value if isinstance(value, bool) else fallback


def _int_value(value: Any, fallback: int) -> int:
    if isinstance(value, bool):
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _optional_int_value(value: Any) -> int | None:
    if value is None:
        return None
    return _int_value(value, 0)


def _date_value(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return value if parsed.isoformat() == value else None
