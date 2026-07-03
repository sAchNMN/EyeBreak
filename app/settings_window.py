from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox

from app.config import AppConfig
from app.icons import apply_window_icon


class SettingsWindow:
    def __init__(
        self,
        master: tk.Tk,
        config: AppConfig,
        on_save: Callable[[AppConfig], None],
        on_close: Callable[[], None],
    ) -> None:
        self.master = master
        self.config = config
        self.on_save = on_save
        self.on_close = on_close
        self.root = tk.Toplevel(master)
        self.entries: dict[str, tk.Entry] = {}
        self._build_window()

    def show(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def focus(self) -> None:
        if self.root.winfo_exists():
            self.show()

    def _build_window(self) -> None:
        self.root.title("EyeBreak 设置")
        apply_window_icon(self.root)
        self.root.geometry("360x280")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f7fb")
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        container = tk.Frame(self.root, bg="#f5f7fb", padx=22, pady=18)
        container.pack(fill=tk.BOTH, expand=True)

        self._add_number_row(
            container,
            "提醒间隔（分钟）",
            "reminder_interval_minutes",
            self.config.reminder_interval_minutes,
            0,
        )
        self._add_number_row(
            container,
            "休息时长（秒）",
            "break_duration_seconds",
            self.config.break_duration_seconds,
            1,
        )
        self._add_number_row(
            container,
            "默认暂停（分钟）",
            "pause_minutes",
            self.config.pause_minutes,
            2,
        )
        self._add_number_row(
            container,
            "离开检测（分钟，0为关闭）",
            "idle_threshold_minutes",
            self.config.idle_threshold_minutes,
            3,
        )

        button_frame = tk.Frame(container, bg="#f5f7fb")
        button_frame.grid(row=4, column=0, columnspan=2, sticky="e", pady=(18, 0))
        tk.Button(button_frame, text="取消", width=9, command=self._close).pack(
            side=tk.LEFT,
            padx=(0, 8),
        )
        tk.Button(button_frame, text="保存", width=9, command=self._save).pack(
            side=tk.LEFT,
        )

    def _add_number_row(
        self,
        parent: tk.Frame,
        label: str,
        key: str,
        value: float | int,
        row: int,
    ) -> None:
        tk.Label(
            parent,
            text=label,
            font=("Microsoft YaHei UI", 10),
            bg="#f5f7fb",
            fg="#1f2937",
        ).grid(row=row, column=0, sticky="w", pady=7)

        entry = tk.Entry(parent, width=12, font=("Microsoft YaHei UI", 10))
        entry.insert(0, _format_number(value))
        entry.grid(row=row, column=1, sticky="e", pady=7)
        self.entries[key] = entry

    def _save(self) -> None:
        try:
            config = parse_settings_values(
                self.entries["reminder_interval_minutes"].get(),
                self.entries["break_duration_seconds"].get(),
                self.entries["pause_minutes"].get(),
                self.entries["idle_threshold_minutes"].get(),
            )
        except ValueError as exc:
            messagebox.showerror("设置无效", str(exc), parent=self.root)
            return

        self.on_save(config)
        self._close()

    def _close(self) -> None:
        if self.root.winfo_exists():
            self.root.destroy()
        self.on_close()


def parse_settings_values(
    reminder_interval_minutes: str,
    break_duration_seconds: str,
    pause_minutes: str,
    idle_threshold_minutes: str,
) -> AppConfig:
    return AppConfig(
        reminder_interval_minutes=_positive_float(
            reminder_interval_minutes,
            "提醒间隔必须大于 0",
        ),
        break_duration_seconds=_positive_int(
            break_duration_seconds,
            "休息时长必须是大于 0 的整数",
        ),
        pause_minutes=_positive_float(
            pause_minutes,
            "默认暂停必须大于 0",
        ),
        idle_threshold_minutes=_non_negative_float(
            idle_threshold_minutes,
            "离开检测不能小于 0",
        ),
    )


def _positive_float(value: str, message: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(message) from exc
    if parsed <= 0:
        raise ValueError(message)
    return parsed


def _positive_int(value: str, message: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(message) from exc
    if parsed <= 0:
        raise ValueError(message)
    return parsed


def _non_negative_float(value: str, message: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(message) from exc
    if parsed < 0:
        raise ValueError(message)
    return parsed


def _format_number(value: float | int) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
