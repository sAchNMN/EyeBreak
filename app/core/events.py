"""Domain event definitions for the EventBus.

All events are frozen dataclasses — they carry immutable payload
from the publisher to subscribers. The EventBus routes them by type.
"""

from __future__ import annotations

from dataclasses import dataclass


# ── Timer lifecycle events ──────────────────────────────────────


@dataclass(frozen=True)
class TimerStarted:
    """Published when the timer engine begins running."""


@dataclass(frozen=True)
class TimerStopped:
    """Published when the timer engine stops (user exit)."""


@dataclass(frozen=True)
class Tick:
    """Published every second with the current countdown snapshot.

    Attributes:
        remaining_seconds: Seconds until next reminder (negative if overdue).
        display_text: Pre-formatted display string (e.g. "24:59", "--:--").
        display_color: Hex color for the countdown label.
    """

    remaining_seconds: float
    display_text: str
    display_color: str


# ── Reminder events ─────────────────────────────────────────────


@dataclass(frozen=True)
class ReminderTriggered:
    """Published when a break reminder fires.

    Attributes:
        duration_seconds: How long the break should last.
        pause_minutes: Default pause duration offered in the reminder.
    """

    duration_seconds: int
    pause_minutes: float


@dataclass(frozen=True)
class ReminderDismissed:
    """Published when the reminder window closes (skip / pause / exit)."""


# ── State change events ─────────────────────────────────────────


@dataclass(frozen=True)
class StateChanged:
    """Published on every state machine transition.

    Attributes:
        old_state: Previous state name.
        new_state: Current state name.
    """

    old_state: str
    new_state: str


@dataclass(frozen=True)
class IdleDetected:
    """Published when the user goes idle (away from keyboard)."""


@dataclass(frozen=True)
class IdleEnded:
    """Published when the user returns from idle."""


@dataclass(frozen=True)
class FullscreenDetected:
    """Published when a fullscreen application is foregrounded."""


@dataclass(frozen=True)
class FullscreenEnded:
    """Published when the fullscreen application exits."""


@dataclass(frozen=True)
class Paused:
    """Published when the timer is paused.

    Attributes:
        paused_until: monotonic timestamp when pause expires.
        pause_minutes: Duration of the pause in minutes.
    """

    paused_until: float
    pause_minutes: float


@dataclass(frozen=True)
class Resumed:
    """Published when the timer resumes from pause."""


# ── Config events ───────────────────────────────────────────────


@dataclass(frozen=True)
class ConfigChanged:
    """Published when user settings are saved.

    Attributes:
        reminder_interval_minutes: New interval value.
        break_duration_seconds: New break duration.
        pause_minutes: New default pause.
        idle_threshold_minutes: New idle threshold.
        fullscreen_detection_enabled: New fullscreen flag.
    """

    reminder_interval_minutes: float
    break_duration_seconds: int
    pause_minutes: float
    idle_threshold_minutes: float
    fullscreen_detection_enabled: bool


# ── UI action events ────────────────────────────────────────────


@dataclass(frozen=True)
class FloatingCountdownToggled:
    """Published when the floating window is enabled/disabled.

    Attributes:
        enabled: New enabled state.
    """

    enabled: bool


@dataclass(frozen=True)
class ExitRequested:
    """Published when the user requests exit (tray → quit)."""
