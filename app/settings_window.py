from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox

from app.config import AppConfig
from app.icons import apply_window_icon
from app.stats import UsageStats, format_completion_rate


class SettingsWindow:
    def __init__(
        self,
        master: tk.Tk,
        config: AppConfig,
        on_save: Callable[[AppConfig], None],
        on_close: Callable[[], None],
        stats: UsageStats | None = None,
        on_reset_stats: Callable[[], None] | None = None,
    ) -> None:
        self.master = master
        self.config = config
        self.on_save = on_save
        self.on_close = on_close
        self.stats = stats or UsageStats()
        self.on_reset_stats = on_reset_stats or (lambda: None)
        self._stats_labels: dict[str, tk.Label] = {}
        self.root = tk.Toplevel(master)
        self.entries: dict[str, tk.Entry] = {}
        self.fullscreen_detection_enabled = tk.BooleanVar(
            value=config.fullscreen_detection_enabled
        )
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
        self.root.geometry("430x500")
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
        tk.Checkbutton(
            container,
            text="全屏时延后提醒",
            variable=self.fullscreen_detection_enabled,
            bg="#f5f7fb",
            fg="#1f2937",
            activebackground="#f5f7fb",
            font=("Microsoft YaHei UI", 10),
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 2))

        self._build_stats(container)

        button_frame = tk.Frame(container, bg="#f5f7fb")
        button_frame.grid(row=6, column=0, columnspan=2, sticky="e", pady=(18, 0))
        tk.Button(button_frame, text="取消", width=9, command=self._close).pack(
            side=tk.LEFT,
            padx=(0, 8),
        )
        tk.Button(button_frame, text="保存", width=9, command=self._save).pack(
            side=tk.LEFT,
        )

    def _build_stats(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(
            parent,
            text="本地统计",
            bg="#f5f7fb",
            fg="#1f2937",
            font=("Microsoft YaHei UI", 10),
            padx=10,
            pady=6,
        )
        frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        for row, key in enumerate(
            ("reminder_count", "completed_count", "skip_count", "pause_count", "rate")
        ):
            label = tk.Label(
                frame,
                bg="#f5f7fb",
                fg="#374151",
                anchor="w",
                font=("Microsoft YaHei UI", 9),
            )
            label.grid(row=row, column=0, sticky="w", pady=1)
            self._stats_labels[key] = label
        tk.Button(
            frame,
            text="清空统计",
            width=9,
            command=self._reset_stats,
        ).grid(row=0, column=1, rowspan=5, padx=(18, 0))
        self._render_stats()

    def _render_stats(self) -> None:
        labels = self._stats_labels
        if not labels:
            return
        labels["reminder_count"].configure(text=f"计划提醒：{self.stats.reminder_count} 次")
        labels["completed_count"].configure(text=f"倒计时完成：{self.stats.completed_count} 次")
        labels["skip_count"].configure(text=f"主动跳过：{self.stats.skip_count} 次")
        labels["pause_count"].configure(text=f"暂停：{self.stats.pause_count} 次")
        labels["rate"].configure(text=f"倒计时完成率：{format_completion_rate(self.stats)}")

    def _reset_stats(self) -> None:
        if not messagebox.askyesno(
            "清空统计", "确定要清空本地统计吗？", parent=self.root
        ):
            return
        self.on_reset_stats()
        self.stats = UsageStats()
        self._render_stats()

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
                self.fullscreen_detection_enabled.get(),
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
    fullscreen_detection_enabled: bool = True,
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
        fullscreen_detection_enabled=fullscreen_detection_enabled,
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
