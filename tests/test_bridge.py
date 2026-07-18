"""Tests for app.ui.bridge.EyeBreakBridge.

Uses minimal stubs for heavy GUI classes (FloatingCountdownWindow,
ReminderWindow, TrayIcon, SettingsWindow) so tests are fast and do
not require a Windows desktop with a display.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

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
from app.core.state_machine import TimerState, StateMachine
from app.core.timer_engine import TimerEngine
from app.state import AppState


# ── Stubs ──────────────────────────────────────────────────────────


class _StubAutostartManager:
    def is_enabled(self) -> bool:
        return False
    def set_enabled(self, enabled: bool) -> None:
        pass


class _StubFloating:
    def __init__(self) -> None:
        self.status_label = MagicMock()
        self.set_enabled = MagicMock()
        self.placement = MagicMock(return_value=("right", 100, 200))


class _StubTray:
    update_menu = MagicMock()
    stop = MagicMock()
    start = MagicMock()


class _StubIdleDetector:
    def get_idle_seconds(self) -> float:
        return 0.0


class _StubFullscreenDetector:
    def is_foreground_fullscreen(self) -> bool:
        return False


# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def root() -> MagicMock:
    r = MagicMock()
    r.winfo_exists = MagicMock(return_value=True)
    return r


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
def engine(bus: EventBus) -> TimerEngine:
    sm = StateMachine(bus)
    idle = _StubIdleDetector()
    fs = _StubFullscreenDetector()
    autostart = _StubAutostartManager()
    config = AppConfig()
    state = AppState()
    return TimerEngine(bus, sm, idle, fs, autostart, config, state)


@pytest.fixture
def bridge(root, bus, engine) -> MagicMock:
    """Return an EyeBreakBridge with heavy UI classes stubbed out."""
    from app.ui.bridge import EyeBreakBridge

    b = EyeBreakBridge(root, bus, engine, engine.state, _StubAutostartManager())
    b.floating = _StubFloating()
    b.floating_label = MagicMock()
    b.tray = _StubTray()
    b.settings = None
    return b


# ── Tick → label update ────────────────────────────────────────────


def test_on_tick_updates_floating_label(bridge) -> None:
    event = Tick(remaining_seconds=120.0, display_text="02:00", display_color="#f9fafb")
    bridge._on_tick(event)
    bridge.floating_label.configure.assert_called_once_with(
        text="02:00", fg="#f9fafb"
    )


def test_on_tick_no_floating_label(bridge) -> None:
    bridge.floating_label = None
    event = Tick(remaining_seconds=0.0, display_text="00:00", display_color="#fff")
    bridge._on_tick(event)  # should not crash


# ── Reminder lifecycle ─────────────────────────────────────────────


@patch("app.ui.bridge.ReminderWindow")
def test_on_reminder_triggered_opens_window(mock_rw, bridge, root) -> None:
    bridge.engine._sm.transition_to(TimerState.SHOWING_REMINDER)
    event = ReminderTriggered(duration_seconds=20, pause_minutes=5.0)

    bridge._on_reminder_triggered(event)

    mock_rw.assert_called_once_with(
        duration_seconds=20,
        pause_minutes=5.0,
        on_skip=bridge.engine.skip_reminder,
        on_pause=mock_rw.call_args.kwargs.get("on_pause"),
        on_exit=mock_rw.call_args.kwargs.get("on_exit"),
        master=root,
    )
    mock_rw.return_value.show.assert_called_once()


def test_on_reminder_triggered_stale_event(bridge) -> None:
    """Should not open window if engine not in SHOWING_REMINDER."""
    event = ReminderTriggered(duration_seconds=20, pause_minutes=5.0)
    bridge._on_reminder_triggered(event)  # should not crash, no window


def test_on_reminder_dismissed_is_noop(bridge) -> None:
    bridge._on_reminder_dismissed(ReminderDismissed())  # should not crash


# ── Status label updates ────────────────────────────────────────────


@pytest.mark.parametrize(
    "handler_name,event_cls,event_kwargs,expected_text,expected_color",
    [
        ("_on_paused", Paused, {"paused_until": 100.0, "pause_minutes": 5.0}, "暂停中", "#fbbf24"),
        ("_on_resumed", Resumed, {}, "下次护眼提醒", "#a7f3d0"),
        ("_on_idle_detected", IdleDetected, {}, "已离开", "#9ca3af"),
        ("_on_idle_ended", IdleEnded, {}, "下次护眼提醒", "#a7f3d0"),
        ("_on_fullscreen_detected", FullscreenDetected, {}, "全屏中", "#60a5fa"),
        ("_on_fullscreen_ended", FullscreenEnded, {}, "下次护眼提醒", "#a7f3d0"),
    ],
)
def test_status_handlers(
    bridge, handler_name, event_cls, event_kwargs, expected_text, expected_color
) -> None:
    handler = getattr(bridge, handler_name)
    event = event_cls(**event_kwargs)
    handler(event)
    bridge.floating.status_label.configure.assert_called_once_with(
        text=expected_text, fg=expected_color
    )


def test_set_status_no_floating(bridge) -> None:
    bridge.floating = None
    bridge._set_status("test", "#fff")  # should not crash


def test_set_status_no_status_label(bridge) -> None:
    bridge.floating.status_label = None
    bridge._set_status("test", "#fff")  # should not crash


# ── Settings window lifecycle ───────────────────────────────────────


@patch("app.ui.bridge.SettingsWindow")
def test_open_settings_creates_new_window(mock_sw, bridge, root) -> None:
    bridge._open_settings()
    mock_sw.assert_called_once_with(
        root,
        bridge.engine.config,
        bridge._save_settings,
        bridge._clear_settings_window,
    )
    mock_sw.return_value.show.assert_called_once()


@patch("app.ui.bridge.SettingsWindow")
def test_open_settings_refocuses_existing(mock_sw, bridge) -> None:
    existing = MagicMock()
    existing.root.winfo_exists.return_value = True
    bridge.settings = existing

    bridge._open_settings()
    existing.focus.assert_called_once()
    mock_sw.assert_not_called()


@patch("app.ui.bridge.save_config")
def test_save_config_persists(mock_save, bridge, engine) -> None:
    new_cfg = AppConfig(reminder_interval_minutes=10)
    bridge._save_settings(new_cfg)
    # Engine in-memory update
    assert engine.config.reminder_interval_minutes == 10
    # Disk persistence
    mock_save.assert_called_once_with(new_cfg)


def test_clear_settings_window(bridge) -> None:
    bridge.settings = MagicMock()
    bridge._clear_settings_window()
    assert bridge.settings is None


# ── Floating countdown toggle ───────────────────────────────────────


def test_on_floating_toggled_enabled(bridge) -> None:
    bridge._on_floating_toggled(FloatingCountdownToggled(enabled=False))
    bridge.floating.set_enabled.assert_called_once_with(False)
    bridge.tray.update_menu.assert_called_once()


def test_on_floating_toggled_no_widgets(bridge) -> None:
    bridge.floating = None
    bridge.tray = None
    bridge._on_floating_toggled(FloatingCountdownToggled(enabled=True))


# ── Config changed handler ─────────────────────────────────────────


def test_on_config_changed_is_safe(bridge) -> None:
    bridge._on_config_changed(ConfigChanged(
        reminder_interval_minutes=10,
        break_duration_seconds=30,
        pause_minutes=15.0,
        idle_threshold_minutes=3.0,
        fullscreen_detection_enabled=True,
    ))


# ── Main tick loop ──────────────────────────────────────────────────


def test_main_tick_calls_engine_tick(bridge, root) -> None:
    bridge._main_tick()
    assert root.after.called
    call_args = root.after.call_args[0]
    assert call_args[0] == 1000
    assert call_args[1].__func__ is bridge._main_tick.__func__


def test_main_tick_terminal_returns_early(bridge, root) -> None:
    bridge.engine.request_exit()  # transitions to EXITED
    root.reset_mock()
    bridge._main_tick()
    root.after.assert_not_called()


# ── Timer stopped / cleanup ────────────────────────────────────────


@patch("app.ui.bridge.save_app_state")
def test_on_timer_stopped_saves_position_and_cleans_up(
    mock_save_state, bridge, root
) -> None:
    bridge._on_timer_stopped(TimerStopped())

    # Position captured from floating
    assert bridge.engine.state.floating_countdown_edge == "right"
    assert bridge.engine.state.floating_countdown_x == 100
    assert bridge.engine.state.floating_countdown_y == 200

    mock_save_state.assert_called_once_with(bridge.engine.state)
    bridge.tray.stop.assert_called_once()
    root.destroy.assert_called_once()


@patch("app.ui.bridge.save_app_state")
def test_on_timer_stopped_no_floating(mock_save_state, bridge, root) -> None:
    bridge.floating = None
    bridge._on_timer_stopped(TimerStopped())
    mock_save_state.assert_called_once()
    root.destroy.assert_called_once()


@patch("app.ui.bridge.save_app_state")
def test_on_timer_stopped_no_tray(mock_save_state, bridge, root) -> None:
    bridge.tray = None
    bridge._on_timer_stopped(TimerStopped())
    mock_save_state.assert_called_once()
    root.destroy.assert_called_once()


# ── UI thread scheduling ───────────────────────────────────────────


def test_ui_thread_schedules_callback(bridge, root) -> None:
    cb = MagicMock()
    bridge._ui_thread(cb)
    root.after.assert_called_once_with(0, cb)


# ── Event wiring (integration via EventBus) ────────────────────────


@patch("app.ui.bridge.save_app_state")
@patch("app.ui.bridge.ReminderWindow")
def test_bridge_subscribes_to_all_events(
    mock_rw, mock_save_state, root, bus, engine
) -> None:
    """Verify that after build(), the bridge responds to every event type."""
    from app.ui.bridge import EyeBreakBridge

    b = EyeBreakBridge(root, bus, engine, engine.state, _StubAutostartManager())
    b.floating = _StubFloating()
    b.floating_label = MagicMock()
    b.tray = _StubTray()
    b.settings = None
    b._wire_events()

    events: list = [
        Tick(120.0, "02:00", "#fff"),
        ReminderTriggered(20, 5.0),
        ReminderDismissed(),
        Paused(paused_until=100.0, pause_minutes=5.0),
        Resumed(),
        IdleDetected(),
        IdleEnded(),
        FullscreenDetected(),
        FullscreenEnded(),
        TimerStopped(),
        FloatingCountdownToggled(True),
        ConfigChanged(10, 30, 15.0, 3.0, True),
    ]
    for event in events:
        bus.publish(event)  # should not crash or raise

@patch("app.ui.bridge.SettingsWindow")
def test_activate_existing_session_opens_or_focuses_settings(mock_sw, bridge) -> None:
    bridge.activate_existing_session()

    mock_sw.return_value.show.assert_called_once_with()

    bridge.settings = mock_sw.return_value
    bridge.settings.root.winfo_exists.return_value = True
    bridge.activate_existing_session()

    bridge.settings.focus.assert_called_once_with()
    assert mock_sw.call_count == 1

def test_build_applies_persisted_floating_enabled_state(bridge) -> None:
    from unittest.mock import MagicMock, patch

    bridge._state.floating_countdown_enabled = False
    bridge._build_floating = MagicMock()
    bridge._wire_events = MagicMock()
    bridge._build_tray = MagicMock()
    bridge._main_tick = MagicMock()
    bridge.engine.start = MagicMock()

    with (
        patch("app.ui.bridge.set_windows_app_user_model_id"),
        patch("app.ui.bridge.ensure_icon_file"),
        patch("app.ui.bridge.apply_window_icon"),
    ):
        bridge.build()

    bridge.floating.set_enabled.assert_called_once_with(False)