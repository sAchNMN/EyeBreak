"""Explicit state machine for the EyeBreak timer.

Replaces the implicit boolean-flag soup (is_showing_reminder, _was_idle,
_was_fullscreen, paused_until) with a single authoritative state enum
and a validated transition table.

Every transition publishes a ``StateChanged`` event on the EventBus,
so UI components can react without being called directly.
"""

from __future__ import annotations

from enum import Enum, auto

from app.core.event_bus import EventBus
from app.core.events import StateChanged


class TimerState(Enum):
    """The six mutually-exclusive operational states."""

    RUNNING = auto()
    IDLE = auto()
    FULLSCREEN = auto()
    PAUSED = auto()
    SHOWING_REMINDER = auto()
    EXITED = auto()


# Allowed (from_state, to_state) pairs.
# Any pair not in this set raises ``IllegalTransition``.
_ALLOWED_TRANSITIONS: frozenset[tuple[TimerState, TimerState]] = frozenset(
    {
        # ── From RUNNING ──
        (TimerState.RUNNING, TimerState.IDLE),
        (TimerState.RUNNING, TimerState.FULLSCREEN),
        (TimerState.RUNNING, TimerState.PAUSED),
        (TimerState.RUNNING, TimerState.SHOWING_REMINDER),
        (TimerState.RUNNING, TimerState.EXITED),
        # ── From IDLE ──
        (TimerState.IDLE, TimerState.RUNNING),
        (TimerState.IDLE, TimerState.PAUSED),
        (TimerState.IDLE, TimerState.EXITED),
        # ── From FULLSCREEN ──
        (TimerState.FULLSCREEN, TimerState.RUNNING),
        (TimerState.FULLSCREEN, TimerState.PAUSED),
        (TimerState.FULLSCREEN, TimerState.EXITED),
        # ── From PAUSED ──
        (TimerState.PAUSED, TimerState.RUNNING),
        (TimerState.PAUSED, TimerState.SHOWING_REMINDER),
        (TimerState.PAUSED, TimerState.EXITED),
        # ── From SHOWING_REMINDER ──
        (TimerState.SHOWING_REMINDER, TimerState.RUNNING),
        (TimerState.SHOWING_REMINDER, TimerState.PAUSED),
        (TimerState.SHOWING_REMINDER, TimerState.EXITED),
        # ── EXITED is terminal ──
    }
)


class IllegalTransition(Exception):
    """Raised when a state transition is not in the allowed set."""

    def __init__(self, from_state: TimerState, to_state: TimerState) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Illegal state transition: {from_state.name} -> {to_state.name}"
        )


class StateMachine:
    """Authoritative state holder with transition validation.

    The state machine is the single source of truth for "what mode
    is the timer in right now". All state reads go through
    ``current_state``; all state writes go through ``transition_to``.
    """

    def __init__(self, bus: EventBus, initial: TimerState = TimerState.RUNNING) -> None:
        self._bus = bus
        self._state = initial

    @property
    def current_state(self) -> TimerState:
        return self._state

    def transition_to(self, new_state: TimerState) -> bool:
        """Attempt to transition to *new_state*.

        Returns ``True`` if the transition succeeded.
        Returns ``False`` if the transition is not allowed (no exception
        raised — callers can choose to ignore or log).

        Publishes a ``StateChanged`` event on success.
        """
        if self._state is new_state:
            return True  # No-op transition is always legal.

        key = (self._state, new_state)
        if key not in _ALLOWED_TRANSITIONS:
            raise IllegalTransition(self._state, new_state)

        old = self._state
        self._state = new_state
        self._bus.publish(StateChanged(old_state=old.name, new_state=new_state.name))
        return True

    def can_transition_to(self, new_state: TimerState) -> bool:
        """Check whether a transition is legal without performing it."""
        if self._state is new_state:
            return True
        return (self._state, new_state) in _ALLOWED_TRANSITIONS

    @property
    def is_terminal(self) -> bool:
        """True once the EXITED state is reached."""
        return self._state is TimerState.EXITED
