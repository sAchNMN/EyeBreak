from __future__ import annotations

import tkinter as tk
from collections.abc import Callable


class ReminderWindow:
    MIN_PAUSE_MINUTES = 1
    MAX_PAUSE_MINUTES = 120
    PAUSE_STEP_MINUTES = 5

    def __init__(
        self,
        duration_seconds: int,
        pause_minutes: float,
        on_skip: Callable[[], None],
        on_pause: Callable[[int], None],
        on_exit: Callable[[], None],
        master: tk.Tk | None = None,
    ) -> None:
        self.duration_seconds = duration_seconds
        self.remaining_seconds = duration_seconds
        self.pause_minutes = self._clamp_pause_minutes(round(pause_minutes))
        self.on_skip = on_skip
        self.on_pause = on_pause
        self.on_exit = on_exit
        self.master = master
        self.root = tk.Toplevel(master) if master else tk.Tk()
        self._build_window()

    def show(self) -> None:
        self._tick()
        if self.master:
            self.root.wait_window()
            return
        self.root.mainloop()

    def _build_window(self) -> None:
        self.root.title("EyeBreak")
        self.root.geometry("460x280")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f7fb")
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self._skip)
        self._center_window(460, 280)

        title = tk.Label(
            self.root,
            text=f"休息 {self.duration_seconds} 秒",
            font=("Microsoft YaHei UI", 24, "bold"),
            bg="#f5f7fb",
            fg="#1f2937",
        )
        title.pack(pady=(30, 8))

        message = tk.Label(
            self.root,
            text="请看 6 米以外的地方",
            font=("Microsoft YaHei UI", 14),
            bg="#f5f7fb",
            fg="#374151",
        )
        message.pack(pady=(0, 18))

        self.countdown_label = tk.Label(
            self.root,
            text=str(self.remaining_seconds),
            font=("Microsoft YaHei UI", 42, "bold"),
            bg="#f5f7fb",
            fg="#111827",
        )
        self.countdown_label.pack(pady=(0, 22))

        button_frame = tk.Frame(self.root, bg="#f5f7fb")
        button_frame.pack()

        self._button(button_frame, "跳过本次", self._skip).pack(side=tk.LEFT, padx=6)
        self.pause_button = self._button(
            button_frame,
            self._pause_button_text(),
            self._pause,
        )
        self.pause_button.pack(side=tk.LEFT, padx=6)
        self.pause_button.bind("<MouseWheel>", self._adjust_pause_minutes)
        self.pause_button.bind("<Button-4>", self._adjust_pause_minutes)
        self.pause_button.bind("<Button-5>", self._adjust_pause_minutes)
        self._button(button_frame, "退出", self._exit).pack(side=tk.LEFT, padx=6)

    def _button(
        self,
        parent: tk.Frame,
        text: str,
        command: Callable[[], None],
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=10,
            font=("Microsoft YaHei UI", 10),
        )

    def _center_window(self, width: int, height: int) -> None:
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _tick(self) -> None:
        self.countdown_label.configure(text=str(self.remaining_seconds))
        if self.remaining_seconds <= 0:
            self._skip()
            return

        self.remaining_seconds -= 1
        self.root.after(1000, self._tick)

    def _skip(self) -> None:
        self.on_skip()
        self.root.destroy()

    def _pause(self) -> None:
        self.on_pause(self.pause_minutes)
        self.root.destroy()

    def _exit(self) -> None:
        self.on_exit()
        self.root.destroy()

    def _adjust_pause_minutes(self, event: tk.Event) -> str:
        direction = 1
        if getattr(event, "num", None) == 5 or getattr(event, "delta", 0) < 0:
            direction = -1

        self.pause_minutes = self._clamp_pause_minutes(
            self.pause_minutes + direction * self.PAUSE_STEP_MINUTES
        )
        self.pause_button.configure(text=self._pause_button_text())
        return "break"

    def _pause_button_text(self) -> str:
        if self.pause_minutes >= 60 and self.pause_minutes % 60 == 0:
            return f"暂停{self.pause_minutes // 60}小时"
        return f"暂停{self.pause_minutes}分钟"

    def _clamp_pause_minutes(self, pause_minutes: int) -> int:
        return max(
            self.MIN_PAUSE_MINUTES,
            min(self.MAX_PAUSE_MINUTES, pause_minutes),
        )