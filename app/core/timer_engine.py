"""TimerEngine — pure business logic for the EyeBreak timer.

Replaces the God-class ReminderTimer by extracting all computation
and state management into an event-driven, testable core.

Dependencies
------------
- EventBus, StateMachine (infrastructure)
- IdleDetector, FullscreenDetector, AutostartManager (platform protocols)
- AppConfig, AppState (domain objects — still owned here until Phase 4)

Zero imports from tkinter, pystray, or any UI/platform concrete module.
"""

from __future__ import annotations

import time

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
    TimerStarted,
    TimerStopped,
)
from app.core.state_machine import StateMachine, TimerState
from app.platform.protocols import (
    AutostartManager,
    FullscreenDetector,
    IdleDetector,
)

# ── Utility ─────────────────────────────────────────────────────


def format_seconds(total_seconds: float) -> str:
    """Format *total_seconds* as ``MM:SS``, rounding up.

    Clamps negative values to ``00:00``.
    This is a pure function (no state, no IO) — kept here for now;
    will be deduplicated with app/timer.py in Phase 4.
    """
    clamped_seconds = max(0, int(total_seconds + 0.999))
    minutes, seconds = divmod(clamped_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


# ── Engine ──────────────────────────────────────────────────────


class TimerEngine:
    """Core timer domain logic.

    Owns the timer schedule, publishes domain events on the EventBus,
    and delegates platform-specific operations to injected Protocols.

    All mutable state lives in the owned *config* and *state* objects.
    """

    def __init__(
        self,
        bus: EventBus,
        state_machine: StateMachine,
        idle_detector: IdleDetector,
        fullscreen_detector: FullscreenDetector,
        autostart_manager: AutostartManager,
        config,
        state,
    ) -> None:
        self._bus = bus
        self._sm = state_machine
        self._idle_detector = idle_detector
        self._fullscreen_detector = fullscreen_detector
        self._autostart_manager = autostart_manager
        self._config = config
        self._state = state

        # Internal state tracking for idle/fullscreen edge transitions.
        self._was_idle = False
        self._was_fullscreen = False

    # ── Properties ──────────────────────────────────────────────

    @property
    def config(self):
        return self._config

    @property
    def state(self):
        return self._state

    @property
    def current_state(self) -> TimerState:
        return self._sm.current_state

    @property
    def is_terminal(self) -> bool:
        return self._sm.is_terminal

    @property
    def is_idle(self) -> bool:
        return self._was_idle

    @property
    def is_fullscreen(self) -> bool:
        return self._was_fullscreen

    # ── Main tick (called ~1/s from the UI main loop) ───────────

    def tick(self, now: float) -> None:
        """Execute one tick of the timer loop.

        Checks pause → idle → fullscreen → reminder → publishes Tick.
        This is the single entry point for periodic updates.
        """
        if self._sm.is_terminal:
            return

        # 1. Pause takes priority over everything.
        if self._state.paused_until > now:
            self._bus.publish(self._make_tick(now))
            return

        # 2. Clear an expired pause.
        if self._state.paused_until and self._state.paused_until <= now:
            self._state.paused_until = 0.0

        # 3. Check idle (may transition state machine).
        if self._check_idle():
            self._bus.publish(self._make_tick(now))
            return

        # 4. Check fullscreen (may transition state machine).
        if self._check_fullscreen():
            self._bus.publish(self._make_tick(now))
            return

        # 5. Fire reminder if it's time and not already showing.
        if self._state.next_reminder_at <= now:
            if self._sm.current_state is not TimerState.SHOWING_REMINDER:
                self._trigger_reminder()
            self._schedule_next_reminder()

        # 6. Publish the current tick for the UI to render.
        self._bus.publish(self._make_tick(now))

    # ── User actions (called from UI/tray event handlers) ────────

    def pause(self, minutes: int) -> None:
        """Pause the timer for *minutes*.

        Reschedules the next reminder to fire after the pause ends.
        """
        now = time.monotonic()
        self._state.paused_until = now + minutes * 60
        self._state.next_reminder_at = (
            self._state.paused_until + self._config.reminder_interval_minutes * 60
        )
        self._sm.transition_to(TimerState.PAUSED)
        self._bus.publish(
            Paused(paused_until=self._state.paused_until, pause_minutes=float(minutes))
        )

    def resume(self) -> None:
        """Resume from paused state."""
        self._state.paused_until = 0.0
        self._schedule_next_reminder()
        self._sm.transition_to(TimerState.RUNNING)
        self._bus.publish(Resumed())

    def break_now(self) -> None:
        """Skip directly to a break reminder, bypassing idle/fullscreen suppression.

        Users expect the tray "立即休息" to work regardless of current mode.
        """
        if self._sm.current_state is TimerState.SHOWING_REMINDER:
            return
        self._state.paused_until = 0.0
        self._state.next_reminder_at = time.monotonic()
        self._trigger_reminder()
        self._schedule_next_reminder()

    def skip_reminder(self) -> None:
        """Dismiss the current reminder without pausing.

        Reschedules so the next tick does not re-trigger.
        """
        if self._sm.current_state is TimerState.SHOWING_REMINDER:
            self._sm.transition_to(TimerState.RUNNING)
            self._schedule_next_reminder()
            self._bus.publish(ReminderDismissed())

    def save_config(self, new_config) -> None:
        """Apply a new configuration and recalculate the schedule.

        The caller (UI or infra) is responsible for persisting the
        config to disk — the engine only updates in-memory state and
        publishes ConfigChanged for subscribers to act on.
        """
        self._config = new_config
        now = time.monotonic()
        if self._state.paused_until > now:
            self._state.next_reminder_at = (
                self._state.paused_until + self._config.reminder_interval_minutes * 60
            )
        else:
            self._schedule_next_reminder()
        self._bus.publish(
            ConfigChanged(
                reminder_interval_minutes=new_config.reminder_interval_minutes,
                break_duration_seconds=new_config.break_duration_seconds,
                pause_minutes=new_config.pause_minutes,
                idle_threshold_minutes=new_config.idle_threshold_minutes,
                fullscreen_detection_enabled=new_config.fullscreen_detection_enabled,
            )
        )

    def toggle_floating_countdown(self) -> None:
        """Toggle the floating countdown visibility flag."""
        self._state.floating_countdown_enabled = (
            not self._state.floating_countdown_enabled
        )
        self._bus.publish(
            FloatingCountdownToggled(enabled=self._state.floating_countdown_enabled)
        )

    def toggle_autostart(self) -> None:
        """Toggle OS-level autostart via the platform manager."""
        enabled = not self._autostart_manager.is_enabled()
        self._autostart_manager.set_enabled(enabled)

    def request_exit(self) -> None:
        """Initiate graceful shutdown.

        The engine transitions to EXITED and publishes TimerStopped.
        The UI layer subscribes to TimerStopped and handles teardown
        (saving state, stopping tray, destroying windows).
        """
        self._sm.transition_to(TimerState.EXITED)
        self._bus.publish(TimerStopped())

    def publish_tick(self, now: float) -> None:
        """Publish a fresh Tick event for the current instant.

        Useful when the UI needs an immediate refresh (e.g. floating
        window re-appears after being hidden).
        """
        self._bus.publish(self._make_tick(now))

    # ── Internal helpers ────────────────────────────────────────

    def _check_idle(self) -> bool:
        """Check idle state, manage transitions, and publish events.

        Returns True if the timer should be suppressed (user is away).
        """
        threshold = self._config.idle_threshold_minutes * 60
        if threshold <= 0:
            # Idle detection is disabled — clear any stale idle state.
            if self._was_idle:
                self._was_idle = False
                self._safe_transition(TimerState.RUNNING)
                self._bus.publish(IdleEnded())
            return False

        is_idle = self._idle_detector.get_idle_seconds() >= threshold

        if is_idle and not self._was_idle:
            self._was_idle = True
            self._safe_transition(TimerState.IDLE)
            self._bus.publish(IdleDetected())
        elif not is_idle and self._was_idle:
            self._was_idle = False
            self._schedule_next_reminder()
            self._safe_transition(TimerState.RUNNING)
            self._bus.publish(IdleEnded())

        return is_idle

    def _check_fullscreen(self) -> bool:
        """Check fullscreen state, manage transitions, and publish events.

        Returns True if the timer should be suppressed (fullscreen app).
        """
        if not self._config.fullscreen_detection_enabled:
            if self._was_fullscreen:
                self._was_fullscreen = False
                self._safe_transition(TimerState.RUNNING)
                self._bus.publish(FullscreenEnded())
            return False

        is_fullscreen = self._fullscreen_detector.is_foreground_fullscreen()

        if is_fullscreen and not self._was_fullscreen:
            self._was_fullscreen = True
            self._safe_transition(TimerState.FULLSCREEN)
            self._bus.publish(FullscreenDetected())
        elif not is_fullscreen and self._was_fullscreen:
            self._was_fullscreen = False
            self._schedule_next_reminder()
            self._safe_transition(TimerState.RUNNING)
            self._bus.publish(FullscreenEnded())

        return is_fullscreen

    def _trigger_reminder(self) -> None:
        """Fire a break reminder and publish the ReminderTriggered event."""
        self._sm.transition_to(TimerState.SHOWING_REMINDER)
        self._bus.publish(
            ReminderTriggered(
                duration_seconds=self._config.break_duration_seconds,
                pause_minutes=self._config.pause_minutes,
            )
        )

    def _schedule_next_reminder(self) -> None:
        """Set next_reminder_at based on the current config and monotonic clock."""
        self._state.next_reminder_at = (
            time.monotonic() + self._config.reminder_interval_minutes * 60
        )

    def _safe_transition(self, target: TimerState) -> None:
        """Transition the state machine if legal; otherwise log and skip.

        This is used by idle/fullscreen checks that may fire when the
        engine is in a state (e.g. PAUSED) where the automatic check
        is redundant but harmless to skip.
        """
        if self._sm.can_transition_to(target):
            self._sm.transition_to(target)

    def _make_tick(self, now: float) -> Tick:
        """Build a Tick event from the current state snapshot."""
        if self._was_idle:
            return Tick(-1.0, "--:--", "#9ca3af")
        if self._was_fullscreen:
            return Tick(-1.0, "--:--", "#60a5fa")
        if self._state.paused_until > now:
            remaining = self._state.paused_until - now
            return Tick(remaining, format_seconds(remaining), "#fbbf24")
        remaining = max(0.0, self._state.next_reminder_at - now)
        return Tick(remaining, format_seconds(remaining), "#f9fafb")