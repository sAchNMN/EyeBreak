"""Event-driven bridge between TimerEngine (core) and the Tkinter UI layer.

The bridge subscribes to domain events published by the engine and
updates UI widgets accordingly. It also routes user actions from the
tray icon / settings window back to the engine.

This is the last piece that replaces ReminderTimer's God-Class wiring.
"""

from __future__ import annotations

import time as _time
import tkinter as tk
from collections.abc import Callable

from app.config import AppConfig, save_config
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
from app.core.state_machine import TimerState
from app.core.timer_engine import TimerEngine
from app.floating_countdown import FloatingCountdownWindow
from app.icons import apply_window_icon, ensure_icon_file, set_windows_app_user_model_id
from app.platform.adapters import AutostartManagerAdapter
from app.reminder_window import ReminderWindow
from app.settings_window import SettingsWindow
from app.state import AppState, save_app_state
from app.tray import TrayIcon


class EyeBreakBridge:
    """Wires TimerEngine to the Tkinter UI via event subscriptions.

    Owns the root Tk window, the floating countdown, the tray icon,
    and the settings/reminder window lifecycle.
    """

    def __init__(
        self,
        root: tk.Tk,
        bus: EventBus,
        engine: TimerEngine,
        state: AppState,
        autostart_manager: AutostartManagerAdapter,
    ) -> None:
        self.root = root
        self.bus = bus
        self.engine = engine
        self._state = state
        self._autostart_manager = autostart_manager

        # UI widgets owned by the bridge
        self.floating: FloatingCountdownWindow | None = None
        self.floating_label: tk.Label | None = None
        self.tray: TrayIcon | None = None
        self.settings: SettingsWindow | None = None

        # Unsubscribe handles
        self._unsubs: list[Callable[[], None]] = []

    # ── Build & wire ─────────────────────────────────────────────

    def build(self) -> None:
        """Create all UI widgets and subscribe to engine events."""
        set_windows_app_user_model_id()
        ensure_icon_file()
        apply_window_icon(self.root)

        self._build_floating()
        self._wire_events()
        self._build_tray()
        self.engine.start()
        self._main_tick()  # start the 1-second tick loop

    def _build_floating(self) -> None:
        self.floating = FloatingCountdownWindow(
            self.root,
            initial_edge=self._state.floating_countdown_edge,
            initial_x=self._state.floating_countdown_x,
            initial_y=self._state.floating_countdown_y,
        )
        self.floating_label = self.floating.build(
            on_close=lambda: self._ui_thread(self.engine.request_exit),
            on_show=lambda: self._ui_thread(
                lambda: self.engine.publish_tick(_time.monotonic())
            ),
        )

    def _build_tray(self) -> None:
        self.tray = TrayIcon(
            on_break_now=lambda: self._ui_thread(self.engine.break_now),
            on_pause=lambda minutes: self._ui_thread(
                lambda: self.engine.pause(minutes)
            ),
            on_resume=lambda: self._ui_thread(self.engine.resume),
            on_open_settings=lambda: self._ui_thread(self._open_settings),
            on_toggle_floating=lambda: self._ui_thread(
                self.engine.toggle_floating_countdown
            ),
            get_is_floating_enabled=lambda: self._state.floating_countdown_enabled,
            on_toggle_autostart=lambda: self._ui_thread(
                lambda: (
                    self.engine.toggle_autostart(),
                    self.tray.update_menu() if self.tray else None,
                )
            ),
            get_is_autostart_enabled=self._autostart_manager.is_enabled,
            on_exit=lambda: self._ui_thread(self.engine.request_exit),
        )
        self.tray.start()

    def _wire_events(self) -> None:
        """Subscribe to engine events and keep unsubscribe handles."""
        self._unsubs.append(self.bus.subscribe(Tick, self._on_tick))
        self._unsubs.append(
            self.bus.subscribe(ReminderTriggered, self._on_reminder_triggered)
        )
        self._unsubs.append(
            self.bus.subscribe(ReminderDismissed, self._on_reminder_dismissed)
        )
        self._unsubs.append(self.bus.subscribe(Paused, self._on_paused))
        self._unsubs.append(self.bus.subscribe(Resumed, self._on_resumed))
        self._unsubs.append(self.bus.subscribe(IdleDetected, self._on_idle_detected))
        self._unsubs.append(self.bus.subscribe(IdleEnded, self._on_idle_ended))
        self._unsubs.append(
            self.bus.subscribe(FullscreenDetected, self._on_fullscreen_detected)
        )
        self._unsubs.append(
            self.bus.subscribe(FullscreenEnded, self._on_fullscreen_ended)
        )
        self._unsubs.append(
            self.bus.subscribe(TimerStopped, self._on_timer_stopped)
        )
        self._unsubs.append(
            self.bus.subscribe(
                FloatingCountdownToggled, self._on_floating_toggled
            )
        )
        self._unsubs.append(
            self.bus.subscribe(ConfigChanged, self._on_config_changed)
        )

    # ── Tick → floating window update ────────────────────────────

    def _on_tick(self, event: Tick) -> None:
        if not self.floating_label or not self.floating:
            return
        self.floating_label.configure(text=event.display_text, fg=event.display_color)

    # ── Reminder lifecycle ───────────────────────────────────────

    def _on_reminder_triggered(self, event: ReminderTriggered) -> None:
        if self.engine.current_state is not TimerState.SHOWING_REMINDER:
            return  # stale event
        ReminderWindow(
            duration_seconds=event.duration_seconds,
            pause_minutes=event.pause_minutes,
            on_skip=self.engine.skip_reminder,
            on_pause=lambda m: self.engine.pause(m),
            on_exit=lambda: self.engine.request_exit(),
            master=self.root,
        ).show()

    def _on_reminder_dismissed(self, event: ReminderDismissed) -> None:
        pass  # nothing extra needed — engine already rescheduled

    # ── Status label updates ─────────────────────────────────────

    def _set_status(self, text: str, fg: str) -> None:
        if self.floating and self.floating.status_label:
            self.floating.status_label.configure(text=text, fg=fg)

    def _on_paused(self, event: Paused) -> None:
        self._set_status("暂停中", "#fbbf24")

    def _on_resumed(self, event: Resumed) -> None:
        self._set_status("下次护眼提醒", "#a7f3d0")

    def _on_idle_detected(self, event: IdleDetected) -> None:
        self._set_status("已离开", "#9ca3af")

    def _on_idle_ended(self, event: IdleEnded) -> None:
        self._set_status("下次护眼提醒", "#a7f3d0")

    def _on_fullscreen_detected(self, event: FullscreenDetected) -> None:
        self._set_status("全屏中", "#60a5fa")

    def _on_fullscreen_ended(self, event: FullscreenEnded) -> None:
        self._set_status("下次护眼提醒", "#a7f3d0")

    # ── Settings window lifecycle ─────────────────────────────────

    def _open_settings(self) -> None:
        if self.settings and self.settings.root.winfo_exists():
            self.settings.focus()
            return

        self.settings = SettingsWindow(
            self.root,
            self.engine.config,
            self._save_settings,
            self._clear_settings_window,
        )
        self.settings.show()

    def _save_settings(self, config: AppConfig) -> None:
        self.engine.save_config(config)
        save_config(config)  # persist to disk

    def _clear_settings_window(self) -> None:
        self.settings = None

    # ── Floating countdown toggle ─────────────────────────────────

    def _on_floating_toggled(self, event: FloatingCountdownToggled) -> None:
        """Update the floating window visible state and refresh tray menu."""
        if self.floating:
            self.floating.set_enabled(event.enabled)
        if self.tray:
            self.tray.update_menu()

    # ── Config changed ──────────────────────────────────────────

    def _on_config_changed(self, event: ConfigChanged) -> None:
        """React when config is updated (currently a no-op beyond engine)."""
        pass

    # ── Main tick loop ──────────────────────────────────────────

    def _main_tick(self) -> None:
        """Periodic tick callback — drives the engine's timer loop."""
        if self.engine.is_terminal:
            return
        self.engine.tick(_time.monotonic())
        self.root.after(1000, self._main_tick)

    # ── Exit / cleanup ───────────────────────────────────────────

    def _on_timer_stopped(self, event: TimerStopped) -> None:
        """Handle graceful shutdown — save state, stop tray, destroy root."""
        if self.floating:
            edge, x, y = self.floating.placement()
            self._state.floating_countdown_edge = edge
            self._state.floating_countdown_x = x
            self._state.floating_countdown_y = y
        save_app_state(self._state)  # persist to disk
        if self.tray:
            self.tray.stop()
        if self.root:
            self.root.destroy()

    def _ui_thread(self, callback: Callable[[], None]) -> None:
        """Schedule a callable on the Tk main thread (for tray thread safety)."""
        self.root.after(0, callback)