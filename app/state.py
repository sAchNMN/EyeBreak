from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.paths import runtime_file_path


APP_STATE_PATH = runtime_file_path("app_state.json")
VALID_FLOATING_EDGES = {"left", "right", "top", "bottom"}


@dataclass
class AppState:
    is_running: bool = True
    paused_until: float = 0.0
    next_reminder_at: float = 0.0
    floating_countdown_enabled: bool = True
    floating_countdown_edge: str | None = "right"
    floating_countdown_x: int = 0
    floating_countdown_y: int | None = None


def load_app_state(path: Path = APP_STATE_PATH) -> AppState:
    if not path.exists():
        return AppState()

    try:
        raw_state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppState()

    if not isinstance(raw_state, dict):
        return AppState()

    floating_state = raw_state.get("floating_countdown")
    if not isinstance(floating_state, dict):
        return AppState()

    return AppState(
        floating_countdown_edge=_floating_edge(floating_state.get("edge")),
        floating_countdown_x=_int_value(floating_state.get("x"), 0),
        floating_countdown_y=_optional_int_value(floating_state.get("y")),
    )


def save_app_state(state: AppState, path: Path = APP_STATE_PATH) -> None:
    payload = {
        "floating_countdown": {
            "edge": state.floating_countdown_edge,
            "x": state.floating_countdown_x,
            "y": state.floating_countdown_y,
        }
    }
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        return


def _floating_edge(value: Any) -> str | None:
    if value in VALID_FLOATING_EDGES:
        return str(value)
    if value is None:
        return None
    return "right"


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
