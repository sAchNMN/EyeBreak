from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppState:
    is_running: bool = True
    paused_until: float = 0.0
    next_reminder_at: float = 0.0