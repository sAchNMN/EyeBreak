"""Tests for app.core.state_machine.StateMachine."""

import pytest

from app.core.event_bus import EventBus
from app.core.events import StateChanged
from app.core.state_machine import IllegalTransition, StateMachine, TimerState


# ── Initial state ───────────────────────────────────────────────


def test_default_initial_state_is_running() -> None:
    sm = StateMachine(EventBus())
    assert sm.current_state is TimerState.RUNNING


def test_custom_initial_state() -> None:
    sm = StateMachine(EventBus(), initial=TimerState.PAUSED)
    assert sm.current_state is TimerState.PAUSED


# ── Legal transitions ───────────────────────────────────────────


@pytest.mark.parametrize(
    "from_state, to_state",
    [
        # RUNNING →
        (TimerState.RUNNING, TimerState.IDLE),
        (TimerState.RUNNING, TimerState.FULLSCREEN),
        (TimerState.RUNNING, TimerState.PAUSED),
        (TimerState.RUNNING, TimerState.SHOWING_REMINDER),
        (TimerState.RUNNING, TimerState.EXITED),
        # IDLE →
        (TimerState.IDLE, TimerState.RUNNING),
        (TimerState.IDLE, TimerState.PAUSED),
        (TimerState.IDLE, TimerState.EXITED),
        # FULLSCREEN →
        (TimerState.FULLSCREEN, TimerState.RUNNING),
        (TimerState.FULLSCREEN, TimerState.PAUSED),
        (TimerState.FULLSCREEN, TimerState.EXITED),
        # PAUSED →
        (TimerState.PAUSED, TimerState.RUNNING),
        (TimerState.PAUSED, TimerState.SHOWING_REMINDER),
        (TimerState.PAUSED, TimerState.EXITED),
        # SHOWING_REMINDER →
        (TimerState.SHOWING_REMINDER, TimerState.RUNNING),
        (TimerState.SHOWING_REMINDER, TimerState.PAUSED),
        (TimerState.SHOWING_REMINDER, TimerState.EXITED),
    ],
)
def test_legal_transition_succeeds(from_state: TimerState, to_state: TimerState) -> None:
    sm = StateMachine(EventBus(), initial=from_state)
    assert sm.transition_to(to_state) is True
    assert sm.current_state is to_state


# ── Illegal transitions ─────────────────────────────────────────


@pytest.mark.parametrize(
    "from_state, to_state",
    [
        # Cannot go directly between IDLE and FULLSCREEN
        (TimerState.IDLE, TimerState.FULLSCREEN),
        (TimerState.FULLSCREEN, TimerState.IDLE),
        # Cannot go from IDLE/FULLSCREEN directly to SHOWING_REMINDER
        (TimerState.IDLE, TimerState.SHOWING_REMINDER),
        (TimerState.FULLSCREEN, TimerState.SHOWING_REMINDER),
        # Cannot leave EXITED
        (TimerState.EXITED, TimerState.RUNNING),
        (TimerState.EXITED, TimerState.PAUSED),
        (TimerState.EXITED, TimerState.IDLE),
        (TimerState.EXITED, TimerState.SHOWING_REMINDER),
        # Cannot go from PAUSED to IDLE or FULLSCREEN
        (TimerState.PAUSED, TimerState.IDLE),
        (TimerState.PAUSED, TimerState.FULLSCREEN),
        # Cannot go from SHOWING_REMINDER to IDLE or FULLSCREEN
        (TimerState.SHOWING_REMINDER, TimerState.IDLE),
        (TimerState.SHOWING_REMINDER, TimerState.FULLSCREEN),
    ],
)
def test_illegal_transition_raises(from_state: TimerState, to_state: TimerState) -> None:
    sm = StateMachine(EventBus(), initial=from_state)
    with pytest.raises(IllegalTransition) as exc_info:
        sm.transition_to(to_state)
    assert exc_info.value.from_state is from_state
    assert exc_info.value.to_state is to_state
    # State must not change.
    assert sm.current_state is from_state


# ── No-op transitions ───────────────────────────────────────────


@pytest.mark.parametrize("state", list(TimerState))
def test_same_state_transition_is_noop(state: TimerState) -> None:
    sm = StateMachine(EventBus(), initial=state)
    assert sm.transition_to(state) is True
    assert sm.current_state is state


# ── Event publishing ────────────────────────────────────────────


def test_transition_publishes_state_changed_event() -> None:
    bus = EventBus()
    sm = StateMachine(bus, initial=TimerState.RUNNING)
    events: list[StateChanged] = []
    bus.subscribe(StateChanged, events.append)

    sm.transition_to(TimerState.PAUSED)

    assert len(events) == 1
    assert events[0].old_state == "RUNNING"
    assert events[0].new_state == "PAUSED"


def test_noop_transition_does_not_publish_event() -> None:
    bus = EventBus()
    sm = StateMachine(bus, initial=TimerState.RUNNING)
    events: list[StateChanged] = []
    bus.subscribe(StateChanged, events.append)

    sm.transition_to(TimerState.RUNNING)

    assert events == []


def test_chained_transitions_publish_in_order() -> None:
    bus = EventBus()
    sm = StateMachine(bus, initial=TimerState.RUNNING)
    events: list[StateChanged] = []
    bus.subscribe(StateChanged, events.append)

    sm.transition_to(TimerState.IDLE)
    sm.transition_to(TimerState.RUNNING)
    sm.transition_to(TimerState.SHOWING_REMINDER)
    sm.transition_to(TimerState.RUNNING)

    assert [e.new_state for e in events] == [
        "IDLE",
        "RUNNING",
        "SHOWING_REMINDER",
        "RUNNING",
    ]


# ── can_transition_to ───────────────────────────────────────────


def test_can_transition_to_returns_true_for_legal() -> None:
    sm = StateMachine(EventBus(), initial=TimerState.RUNNING)
    assert sm.can_transition_to(TimerState.PAUSED) is True


def test_can_transition_to_returns_false_for_illegal() -> None:
    sm = StateMachine(EventBus(), initial=TimerState.IDLE)
    assert sm.can_transition_to(TimerState.FULLSCREEN) is False


def test_can_transition_to_returns_true_for_same_state() -> None:
    sm = StateMachine(EventBus(), initial=TimerState.PAUSED)
    assert sm.can_transition_to(TimerState.PAUSED) is True


# ── is_terminal ─────────────────────────────────────────────────


def test_is_terminal_false_before_exit() -> None:
    sm = StateMachine(EventBus(), initial=TimerState.RUNNING)
    assert sm.is_terminal is False


def test_is_terminal_true_after_exit() -> None:
    sm = StateMachine(EventBus(), initial=TimerState.RUNNING)
    sm.transition_to(TimerState.EXITED)
    assert sm.is_terminal is True


def test_cannot_leave_exited_state() -> None:
    sm = StateMachine(EventBus(), initial=TimerState.EXITED)
    with pytest.raises(IllegalTransition):
        sm.transition_to(TimerState.RUNNING)


# ── Real-world transition sequences ─────────────────────────────


def test_typical_work_session_cycle() -> None:
    """Simulates: run → idle → run → reminder → run → pause → run → exit."""
    bus = EventBus()
    sm = StateMachine(bus, initial=TimerState.RUNNING)

    sm.transition_to(TimerState.IDLE)         # User walks away
    sm.transition_to(TimerState.RUNNING)      # User returns
    sm.transition_to(TimerState.SHOWING_REMINDER)  # Timer fires
    sm.transition_to(TimerState.RUNNING)      # Dismiss reminder
    sm.transition_to(TimerState.PAUSED)       # User pauses
    sm.transition_to(TimerState.RUNNING)      # Pause expires
    sm.transition_to(TimerState.EXITED)       # User quits

    assert sm.is_terminal is True


def test_break_now_from_paused() -> None:
    """User pauses, then hits 'break now' from the tray."""
    sm = StateMachine(EventBus(), initial=TimerState.PAUSED)
    sm.transition_to(TimerState.SHOWING_REMINDER)
    sm.transition_to(TimerState.RUNNING)
    assert sm.current_state is TimerState.RUNNING


def test_exit_from_reminder() -> None:
    """User clicks 'exit' from the reminder window."""
    sm = StateMachine(EventBus(), initial=TimerState.SHOWING_REMINDER)
    sm.transition_to(TimerState.EXITED)
    assert sm.is_terminal is True
