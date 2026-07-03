from __future__ import annotations

import time
import tkinter as tk
from collections.abc import Callable

from app.config import AppConfig
from app.floating_countdown import FloatingCountdownWindow
from app.icons import apply_window_icon, ensure_icon_file, set_windows_app_user_model_id
from app.reminder_window import ReminderWindow
from app.state import AppState
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
        self.countdown_window = FloatingCountdownWindow(self.root)
        self.status_label = self.countdown_window.build(self._exit)

    def _start_tray_icon(self) -> None:
        self.tray_icon = TrayIcon(
            on_break_now=lambda: self._run_on_ui_thread(self._break_now),
            on_pause=lambda minutes: self._run_on_ui_thread(lambda: self._pause(minutes)),
            on_resume=lambda: self._run_on_ui_thread(self._resume),
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
            self.status_label.configure(
                text=format_seconds(self.state.paused_until - now),
                fg="#fbbf24",
            )
            self.root.after(1000, self._tick)
            return

        if self.state.paused_until and self.state.paused_until <= now:
            self.state.paused_until = 0.0

        remaining_seconds = self.state.next_reminder_at - now
        if remaining_seconds <= 0:
            self.status_label.configure(text="00:00", fg="#f9fafb")
            self._show_reminder()
            if self.state.is_running and self.state.paused_until <= time.monotonic():
                self._schedule_next_reminder()

            self.root.after(1000, self._tick)
            return

        self.status_label.configure(text=format_seconds(remaining_seconds), fg="#f9fafb")
        self.root.after(1000, self._tick)

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

    def _exit(self) -> None:
        self.state.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
        if self.root:
            self.root.destroy()


def format_seconds(total_seconds: float) -> str:
    clamped_seconds = max(0, int(total_seconds + 0.999))
    minutes, seconds = divmod(clamped_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"
