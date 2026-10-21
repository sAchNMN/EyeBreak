"""Event-driven bridge between TimerEngine (core) and the Tkinter UI layer.

The bridge subscribes to domain events published by the engine and
updates UI widgets accordingly. It also routes user actions from the
tray icon / settings window back to the engine.
"""

from __future__ import annotations

import time as _time
import tkinter as tk
from collections.abc import Callable

from app.config import AppConfig, save_config
from app.core.event_bus import EventBus
from app.core.events import (
    FloatingCountdownToggled,
    FullscreenDetected,
    FullscreenEnded,
    IdleDetected,
    IdleEnded,
    Paused,
    ReminderTriggered,
    Resumed,
    TodayPauseEnded,
    TodayPauseStarted,
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
from app.stats import StatsTracker
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
        self.stats = StatsTracker(bus)

        # UI widgets owned by the bridge
        self.floating: FloatingCountdownWindow | None = None
        self.floating_label: tk.Label | None = None
        self.tray: TrayIcon | None = None
        self.settings: SettingsWindow | None = None

        # Unsubscribe handles
        self._unsubs: list[Callable[[], None]] = []

        # Tray startup diagnostics
        self._tray_check_attempts = 0
        self._tray_warning_shown = False
        self._tray_warning_dialog: tk.Toplevel | None = None

    # ── Build & wire ─────────────────────────────────────────────

    def build(self) -> None:
        """Create all UI widgets and subscribe to engine events."""
        set_windows_app_user_model_id()
        ensure_icon_file()
        apply_window_icon(self.root)

        self._build_floating()
        if self.floating:
            self.floating.set_enabled(self._state.floating_countdown_enabled)
        self._wire_events()
        self._build_tray()
        self.engine.start()
        if self.engine.is_today_paused:
            self._on_today_pause_started(TodayPauseStarted())
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
            on_pause_today=lambda: self._ui_thread(self.engine.pause_today),
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
        self.root.after(700, self._check_tray_status)

    def _check_tray_status(self) -> None:
        """Warn when Windows rejects the tray icon instead of failing silently."""
        if not self.tray or self._tray_warning_shown:
            return

        status = self.tray.last_notify_result()
        if status is None:
            self._tray_check_attempts += 1
            if self._tray_check_attempts < 6:
                self.root.after(400, self._check_tray_status)
            return

        result, _error = status
        if result:
            return

        self._tray_warning_shown = True
        self._show_tray_warning()

    def _show_tray_warning(self) -> None:
        """Show a reliable Tk dialog.

        ``tkinter.messagebox`` returns immediately when the app already owns an
        override-redirect topmost window (the floating countdown), so use a
        plain Toplevel instead.
        """
        dialog = tk.Toplevel(self.root)
        self._tray_warning_dialog = dialog
        dialog.title("EyeBreak 托盘图标")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

        body = tk.Frame(dialog, padx=18, pady=14)
        body.pack(fill="both", expand=True)
        tk.Label(
            body,
            text=(
                "Windows 没有接受 EyeBreak 的托盘图标。\n\n"
                "请退出 EyeBreak，然后从文件资源管理器双击 EyeBreak.exe 重新启动；"
                "不要使用“以管理员身份运行”，也不要在管理员或受限终端中启动。\n\n"
                "如果 icacls EyeBreak.exe 显示 Low Mandatory Level，"
                "说明文件在受限工作区；请把整个 EyeBreak 文件夹复制到桌面或普通目录，"
                "再从副本启动。\n\n"
                "如果图标只是被 Windows 隐藏，请点击任务栏的 ^，"
                "或在“设置 > 个性化 > 任务栏 > 其他系统托盘图标”中打开 EyeBreak。"
            ),
            justify="left",
            anchor="w",
            wraplength=460,
        ).pack(fill="x")
        tk.Button(
            body,
            text="知道了",
            width=10,
            command=dialog.destroy,
        ).pack(pady=(14, 0))

        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() - width) // 2
        y = (dialog.winfo_screenheight() - height) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

    def _wire_events(self) -> None:
        """Subscribe to engine events and keep unsubscribe handles."""
        self._unsubs.append(self.bus.subscribe(Tick, self._on_tick))
        self._unsubs.append(
            self.bus.subscribe(ReminderTriggered, self._on_reminder_triggered)
        )
        self._unsubs.append(self.bus.subscribe(Paused, self._on_paused))
        self._unsubs.append(self.bus.subscribe(Resumed, self._on_resumed))
        self._unsubs.append(
            self.bus.subscribe(TodayPauseStarted, self._on_today_pause_started)
        )
        self._unsubs.append(
            self.bus.subscribe(TodayPauseEnded, self._on_today_pause_ended)
        )
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

    # ── Tick → floating window update ────────────────────────────

    def _on_tick(self, event: Tick) -> None:
        if not self.floating_label or not self.floating:
            return
        if not self.floating.should_update_display():
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
            on_complete=self.engine.complete_reminder,
            on_pause_today=self.engine.pause_today,
        ).show()

    # ── Status label updates ─────────────────────────────────────

    def _set_status(self, text: str, fg: str) -> None:
        if self.floating and self.floating.status_label:
            self.floating.status_label.configure(text=text, fg=fg)

    def _on_paused(self, event: Paused) -> None:
        self._set_status("暂停中", "#fbbf24")

    def _on_resumed(self, event: Resumed) -> None:
        self._set_status("下次护眼提醒", "#a7f3d0")

    def _on_today_pause_started(self, event: TodayPauseStarted) -> None:
        self._set_status("今日免打扰", "#9ca3af")

    def _on_today_pause_ended(self, event: TodayPauseEnded) -> None:
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
            self.stats.stats,
            self.stats.reset,
        )
        self.settings.show()

    def activate_existing_session(self) -> None:
        """Bring the existing session settings window to the foreground."""
        self._open_settings()

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
