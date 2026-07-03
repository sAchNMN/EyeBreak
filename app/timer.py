from __future__ import annotations

import time
import tkinter as tk
from collections.abc import Callable

from app.config import AppConfig
from app.floating_countdown import FloatingCountdownWindow
from app.icons import apply_window_icon, ensure_icon_file, set_windows_app_user_model_id
from app.reminder_window import ReminderWindow
from app.state import AppState, save_app_state
from app.tray import TrayIcon


class ReminderTimer:
    def __init__(self, config: AppConfig, state: AppState) -> None:
        self.config = config
        self.state = state
        self.root: tk.Tk | None = None
        self.status_label: tk.Label | None = None
        self.countdown_window: FloatingCountdownWindow | None = None
        self.tray_icon: TrayIcon | None = None
        self.is_showing_reminder = False

    def run(self) -> None:
        set_windows_app_user_model_id()
        ensure_icon_file()
        self.root = tk.Tk()
        self._build_countdown_window()
        self._schedule_next_reminder()
        self._start_tray_icon()
        self._tick()
        self.root.mainloop()

    def _build_countdown_window(self) -> None:
        if not self.root:
            return

        apply_window_icon(self.root)
        self.countdown_window = FloatingCountdownWindow(
            self.root,
            initial_edge=self.state.floating_countdown_edge,  # type: ignore[arg-type]
            initial_x=self.state.floating_countdown_x,
            initial_y=self.state.floating_countdown_y,
        )
        self.status_label = self.countdown_window.build(
            self._exit,
            on_show=self._update_countdown_display,
        )

    def _start_tray_icon(self) -> None:
        self.tray_icon = TrayIcon(
            on_break_now=lambda: self._run_on_ui_thread(self._break_now),
            on_pause=lambda minutes: self._run_on_ui_thread(lambda: self._pause(minutes)),
            on_resume=lambda: self._run_on_ui_thread(self._resume),
            on_toggle_floating=lambda: self._run_on_ui_thread(
                self._toggle_floating_countdown
            ),
            on_exit=lambda: self._run_on_ui_thread(self._exit),
        )
        self.tray_icon.start()

    def _run_on_ui_thread(self, callback: Callable[[], None]) -> None:
        if self.root and self.state.is_running:
            self.root.after(0, callback)

    def _schedule_next_reminder(self) -> None:
        self.state.next_reminder_at = (
            time.monotonic() + self.config.reminder_interval_minutes * 60
        )

    def _tick(self) -> None:
        if not self.root or not self.status_label:
            return

        if not self.state.is_running:
            self.root.destroy()
            return

        now = time.monotonic()
        if self.state.paused_until > now:
            self._update_countdown_display(now)
            self.root.after(1000, self._tick)
            return

        if self.state.paused_until and self.state.paused_until <= now:
            self.state.paused_until = 0.0

        remaining_seconds = self.state.next_reminder_at - now
        if remaining_seconds <= 0:
            self._configure_countdown_label("00:00", "#f9fafb")
            self._show_reminder()
            if self.state.is_running and self.state.paused_until <= time.monotonic():
                self._schedule_next_reminder()

            self.root.after(1000, self._tick)
            return

        self._update_countdown_display(now)
        self.root.after(1000, self._tick)

    def _update_countdown_display(self, now: float | None = None) -> None:
        if not self._should_update_countdown_display():
            return

        current_time = time.monotonic() if now is None else now
        if self.state.paused_until > current_time:
            if self.countdown_window:
                self.countdown_window.set_paused(True)
            self._configure_countdown_label(
                format_seconds(self.state.paused_until - current_time),
                "#fbbf24",
            )
            return

        if self.countdown_window:
            self.countdown_window.set_paused(False)
        self._configure_countdown_label(
            format_seconds(self.state.next_reminder_at - current_time),
            "#f9fafb",
        )

    def _should_update_countdown_display(self) -> bool:
        if not self.status_label:
            return False
        if not self.countdown_window:
            return True
        return self.countdown_window.should_update_display()

    def _configure_countdown_label(self, text: str, fg: str) -> None:
        if not self._should_update_countdown_display():
            return
        if self.status_label:
            self.status_label.configure(text=text, fg=fg)

    def _show_reminder(self) -> None:
        if not self.root or self.is_showing_reminder:
            return

        self.is_showing_reminder = True
        try:
            ReminderWindow(
                duration_seconds=self.config.break_duration_seconds,
                pause_minutes=self.config.pause_minutes,
                on_skip=self._skip_current,
                on_pause=self._pause,
                on_exit=self._exit,
                master=self.root,
            ).show()
        finally:
            self.is_showing_reminder = False

    def _break_now(self) -> None:
        if self.is_showing_reminder:
            return
        self.state.paused_until = 0.0
        self.state.next_reminder_at = time.monotonic()
        self._show_reminder()
        if self.state.is_running and self.state.paused_until <= time.monotonic():
            self._schedule_next_reminder()

    def _skip_current(self) -> None:
        pass

    def _pause(self, pause_minutes: int) -> None:
        self.state.paused_until = time.monotonic() + pause_minutes * 60
        self.state.next_reminder_at = (
            self.state.paused_until + self.config.reminder_interval_minutes * 60
        )

    def _resume(self) -> None:
        self.state.paused_until = 0.0
        self._schedule_next_reminder()

    def _toggle_floating_countdown(self) -> None:
        self.state.floating_countdown_enabled = not self.state.floating_countdown_enabled
        if self.countdown_window:
            self.countdown_window.set_enabled(self.state.floating_countdown_enabled)

    def _exit(self) -> None:
        self.state.is_running = False
        if self.countdown_window:
            edge, x, y = self.countdown_window.placement()
            self.state.floating_countdown_edge = edge
            self.state.floating_countdown_x = x
            self.state.floating_countdown_y = y
        save_app_state(self.state)
        if self.tray_icon:
            self.tray_icon.stop()
        if self.root:
            self.root.destroy()


def format_seconds(total_seconds: float) -> str:
    clamped_seconds = max(0, int(total_seconds + 0.999))
    minutes, seconds = divmod(clamped_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"