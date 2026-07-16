"""Tests for app.core.timer_engine.TimerEngine.

All platform dependencies are fakes so tests are fast, deterministic,
and do not require a Windows desktop.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import pytest

from app.config import AppConfig
from app.core.event_bus import EventBus
from app.core.events import (
    ConfigChanged,
    FloatingCountdownToggled,
    FullscreenDetected,
    FullscreenEnded,
    IdleDetected,
    IdleEnded,
    Paused,
    ReminderDismissed,
    ReminderTriggered,
    Resumed,
    Tick,
    TimerStopped,
)
from app.core.state_machine import StateMachine, TimerState
from app.core.timer_engine import TimerEngine, format_seconds
from app.state import AppState


# ── Platform fakes ────────────────────────────────────────────────


class FakeIdleDetector:
    def __init__(self, idle_seconds: float = 0.0) -> None:
        self._idle = idle_seconds

    def set_idle_seconds(self, value: float) -> None:
        self._idle = value

    def get_idle_seconds(self) -> float:
        return self._idle


class FakeFullscreenDetector:
    def __init__(self, is_fullscreen: bool = False) -> None:
        self._fullscreen = is_fullscreen

    def set_fullscreen(self, value: bool) -> None:
        self._fullscreen = value

    def is_foreground_fullscreen(self) -> bool:
        return self._fullscreen


class FakeAutostartManager:
    def __init__(self, enabled: bool = False) -> None:
        self._enabled = enabled
        self.set_calls: list[bool] = []

    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.set_calls.append(enabled)


# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
def engine(bus: EventBus) -> TimerEngine:
    idle = FakeIdleDetector()
    fs = FakeFullscreenDetector()
    autostart = FakeAutostartManager()
    config = AppConfig()
    state = AppState(next_reminder_at=600.0)
    sm = StateMachine(bus)
    return TimerEngine(
        bus=bus,
        state_machine=sm,
        idle_detector=idle,
        fullscreen_detector=fs,
        autostart_manager=autostart,
        config=config,
        state=state,
    )


# ── format_seconds ────────────────────────────────────────────────


def test_format_seconds_rounds_up() -> None:
    assert format_seconds(59.1) == "01:00"


def test_format_seconds_exact_minute() -> None:
    assert format_seconds(60.0) == "01:00"


def test_format_seconds_over_minute() -> None:
    assert format_seconds(61.0) == "01:01"


def test_format_seconds_clamps_negative() -> None:
    assert format_seconds(-1.0) == "00:00"


# ── tick: normal flow ────────────────────────────────────────────


def test_tick_publishes_tick_event(bus: EventBus, engine: TimerEngine) -> None:
    ticks: list[Tick] = []
    bus.subscribe(Tick, ticks.append)

    engine.tick(now=100.0)

    assert len(ticks) >= 1
    assert ticks[0].remaining_seconds == 500.0  # 600 - 100


def test_tick_does_nothing_after_exit(bus: EventBus, engine: TimerEngine) -> None:
    engine.request_exit()
    ticks: list[Tick] = []
    bus.subscribe(Tick, ticks.append)

    engine.tick(now=100.0)

    assert ticks == []


# ── tick: pause handling ─────────────────────────────────────────


def test_tick_while_paused_shows_pause_countdown(
    bus: EventBus, engine: TimerEngine
) -> None:
    engine.state.paused_until = 200.0
    ticks: list[Tick] = []
    bus.subscribe(Tick, ticks.append)

    engine.tick(now=100.0)

    assert len(ticks) == 1
    assert ticks[0].remaining_seconds == 100.0  # 200 - 100
    assert ticks[0].display_color == "#fbbf24"


def test_tick_clears_expired_pause(bus: EventBus, engine: TimerEngine) -> None:
    engine.state.paused_until = 50.0  # expired at now = 100
    engine.state.next_reminder_at = 0.0

    engine.tick(now=100.0)

    assert engine.state.paused_until == 0.0
    assert engine.state.next_reminder_at > 0.0  # rescheduled


# ── tick: idle handling ──────────────────────────────────────────


def test_tick_suppressed_by_idle(bus: EventBus, engine: TimerEngine) -> None:
    engine._idle_detector.set_idle_seconds(500.0)  # well above 5-min threshold
    ticks: list[Tick] = []
    bus.subscribe(Tick, ticks.append)

    engine.tick(now=100.0)

    assert ticks[-1].display_text == "--:--"
    assert ticks[-1].display_color == "#9ca3af"
    assert engine._was_idle is True


def test_idle_detected_event_published(bus: EventBus, engine: TimerEngine) -> None:
    events: list = []
    bus.subscribe(IdleDetected, events.append)
    engine._idle_detector.set_idle_seconds(500.0)

    engine.tick(now=100.0)

    assert len(events) == 1


def test_idle_ended_event_published_on_return(
    bus: EventBus, engine: TimerEngine
) -> None:
    events: list = []
    bus.subscribe(IdleEnded, events.append)
    engine._was_idle = True
    engine._idle_detector.set_idle_seconds(0.0)

    engine.tick(now=100.0)

    assert len(events) == 1
    assert engine._was_idle is False


def test_idle_disabled_clears_stale_state(
    bus: EventBus, engine: TimerEngine
) -> None:
    engine._was_idle = True
    engine.save_config(AppConfig(idle_threshold_minutes=0))  # disable
    events: list = []
    bus.subscribe(IdleEnded, events.append)

    engine.tick(now=100.0)

    assert engine._was_idle is False
    assert len(events) == 1


# ── tick: fullscreen handling ────────────────────────────────────


def test_tick_suppressed_by_fullscreen(
    bus: EventBus, engine: TimerEngine
) -> None:
    engine._fullscreen_detector.set_fullscreen(True)
    ticks: list[Tick] = []
    bus.subscribe(Tick, ticks.append)

    engine.tick(now=100.0)

    assert ticks[-1].display_text == "--:--"
    assert ticks[-1].display_color == "#60a5fa"


def test_fullscreen_detected_event_published(
    bus: EventBus, engine: TimerEngine
) -> None:
    events: list = []
    bus.subscribe(FullscreenDetected, events.append)
    engine._fullscreen_detector.set_fullscreen(True)

    engine.tick(now=100.0)

    assert len(events) == 1
    assert engine._was_fullscreen is True


def test_fullscreen_ended_event_published_on_exit(
    bus: EventBus, engine: TimerEngine
) -> None:
    events: list = []
    bus.subscribe(FullscreenEnded, events.append)
    engine._was_fullscreen = True
    engine._fullscreen_detector.set_fullscreen(False)

    engine.tick(now=100.0)

    assert len(events) == 1
    assert engine._was_fullscreen is False


def test_fullscreen_disabled_clears_stale_state(
    bus: EventBus, engine: TimerEngine
) -> None:
    engine._was_fullscreen = True
    engine.save_config(
        AppConfig(
            fullscreen_detection_enabled=False,
            reminder_interval_minutes=engine.config.reminder_interval_minutes,
            break_duration_seconds=engine.config.break_duration_seconds,
            pause_minutes=engine.config.pause_minutes,
            idle_threshold_minutes=engine.config.idle_threshold_minutes,
        )
    )
    events: list = []
    bus.subscribe(FullscreenEnded, events.append)

    engine.tick(now=100.0)

    assert engine._was_fullscreen is False
    assert len(events) == 1


# ── tick: reminder triggering ────────────────────────────────────


def test_tick_triggers_reminder_when_time_elapses(
    bus: EventBus, engine: TimerEngine
) -> None:
    engine.state.next_reminder_at = 100.0  # overdue
    engine.state.paused_until = 0.0
    events: list = []
    bus.subscribe(ReminderTriggered, events.append)

    engine.tick(now=101.0)

    assert len(events) == 1
    assert events[0].duration_seconds == 20
    assert engine.current_state is TimerState.SHOWING_REMINDER


def test_tick_does_not_retrigger_while_showing_reminder(
    bus: EventBus, engine: TimerEngine
) -> None:
    engine.state.next_reminder_at = 0.0  # always overdue
    # First tick triggers it
    events: list = []
    bus.subscribe(ReminderTriggered, events.append)
    engine.tick(now=101.0)
    assert len(events) == 1

    # Second tick should NOT trigger again
    engine.tick(now=102.0)
    assert len(events) == 1


# ── pause / resume ───────────────────────────────────────────────


def test_pause_sets_state_and_publishes_event(
    bus: EventBus, engine: TimerEngine, monkeypatch
) -> None:
    monkeypatch.setattr(time, "monotonic", lambda: 1000.0)
    events: list = []
    bus.subscribe(Paused, events.append)

    engine.pause(minutes=15)

    assert engine.state.paused_until == 1900.0  # 1000 + 15*60
    assert engine.current_state is TimerState.PAUSED
    assert len(events) == 1
    assert isinstance(events[0], Paused)


def test_resume_clears_pause_and_publishes(
    bus: EventBus, engine: TimerEngine, monkeypatch
) -> None:
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    engine.state.paused_until = 200.0
    events: list = []
    bus.subscribe(Resumed, events.append)

    engine.resume()

    assert engine.state.paused_until == 0.0
    assert engine.current_state is TimerState.RUNNING
    assert len(events) == 1


# ── break_now ────────────────────────────────────────────────────


def test_break_now_publishes_reminder(
    bus: EventBus, engine: TimerEngine, monkeypatch
) -> None:
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    events: list = []
    bus.subscribe(ReminderTriggered, events.append)

    engine.break_now()

    assert engine.state.paused_until == 0.0
    assert len(events) == 1
    assert engine.current_state is TimerState.SHOWING_REMINDER


def test_break_now_noop_when_already_showing(
    bus: EventBus, engine: TimerEngine
) -> None:
    engine._sm.transition_to(TimerState.SHOWING_REMINDER)
    events: list = []
    bus.subscribe(ReminderTriggered, events.append)

    engine.break_now()

    assert len(events) == 0  # no duplicate trigger


# ── skip_reminder ────────────────────────────────────────────────


def test_skip_reminder_dismisses_and_reschedules(
    bus: EventBus, engine: TimerEngine, monkeypatch
) -> None:
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    # first trigger a reminder
    engine.state.next_reminder_at = 0.0
    engine.tick(now=101.0)
    events: list = []
    bus.subscribe(ReminderDismissed, events.append)

    engine.skip_reminder()

    assert len(events) == 1
    assert isinstance(events[0], ReminderDismissed)
    assert engine.current_state is TimerState.RUNNING
    assert engine.state.next_reminder_at > 100.0


def test_skip_reminder_noop_when_not_showing(
    bus: EventBus, engine: TimerEngine
) -> None:
    events: list = []
    bus.subscribe(ReminderDismissed, events.append)

    engine.skip_reminder()

    assert len(events) == 0
    assert engine.current_state is TimerState.RUNNING


# ── save_config ──────────────────────────────────────────────────


def test_save_config_updates_internal_config_and_publishes(
    bus: EventBus, engine: TimerEngine, monkeypatch
) -> None:
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    new_config = AppConfig(reminder_interval_minutes=10, break_duration_seconds=30)
    events: list = []
    bus.subscribe(ConfigChanged, events.append)

    engine.save_config(new_config)

    assert engine.config.reminder_interval_minutes == 10
    assert engine.config.break_duration_seconds == 30
    assert len(events) == 1
    ev = events[0]
    assert ev.reminder_interval_minutes == 10
    assert ev.break_duration_seconds == 30


def test_save_config_reschedules_when_not_paused(
    bus: EventBus, engine: TimerEngine, monkeypatch
) -> None:
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    engine.save_config(AppConfig(reminder_interval_minutes=5))
    # next_reminder_at should be now + interval
    assert engine.state.next_reminder_at == 100.0 + 5 * 60


def test_save_config_reschedules_relative_to_pause_end(
    bus: EventBus, engine: TimerEngine, monkeypatch
) -> None:
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    engine.state.paused_until = 500.0

    engine.save_config(AppConfig(reminder_interval_minutes=10))

    # Should be paused_until + interval, not now + interval
    assert engine.state.next_reminder_at == 500.0 + 10 * 60


# ── toggle_floating_countdown ────────────────────────────────────


def test_toggle_floating_countdown_toggles_and_publishes(
    bus: EventBus, engine: TimerEngine
) -> None:
    assert engine.state.floating_countdown_enabled is True
    events: list = []
    bus.subscribe(FloatingCountdownToggled, events.append)

    engine.toggle_floating_countdown()

    assert engine.state.floating_countdown_enabled is False
    assert len(events) == 1
    assert events[0].enabled is False

    engine.toggle_floating_countdown()

    assert engine.state.floating_countdown_enabled is True
    assert len(events) == 2
    assert events[1].enabled is True


# ── toggle_autostart ─────────────────────────────────────────────


def test_toggle_autostart_flips_via_platform(
    bus: EventBus, engine: TimerEngine
) -> None:
    manager = engine._autostart_manager
    assert manager.is_enabled() is False

    engine.toggle_autostart()

    assert manager.set_calls == [True]
    assert manager.is_enabled() is True

    engine.toggle_autostart()

    assert manager.set_calls == [True, False]
    assert manager.is_enabled() is False


# ── request_exit ─────────────────────────────────────────────────


def test_request_exit_transitions_and_publishes(
    bus: EventBus, engine: TimerEngine
) -> None:
    events: list = []
    bus.subscribe(TimerStopped, events.append)

    engine.request_exit()

    assert engine.is_terminal is True
    assert len(events) == 1


def test_request_exit_is_idempotent(
    bus: EventBus, engine: TimerEngine
) -> None:
    engine.request_exit()
    engine.request_exit()  # should not raise
    assert engine.is_terminal is True


# ── publish_tick ─────────────────────────────────────────────────


def test_publish_tick_emits_current_snapshot(
    bus: EventBus, engine: TimerEngine
) -> None:
    ticks: list[Tick] = []
    bus.subscribe(Tick, ticks.append)

    engine.publish_tick(now=100.0)

    assert len(ticks) == 1
    assert ticks[0].remaining_seconds == 500.0


def test_publish_tick_idle(bus: EventBus, engine: TimerEngine) -> None:
    engine._was_idle = True
    ticks: list[Tick] = []
    bus.subscribe(Tick, ticks.append)

    engine.publish_tick(now=100.0)

    assert ticks[0].display_text == "--:--"
    assert ticks[0].display_color == "#9ca3af"