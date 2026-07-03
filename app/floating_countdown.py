from __future__ import annotations

import tkinter as tk
from collections.abc import Callable


WINDOW_WIDTH = 188
WINDOW_HEIGHT = 64
VISIBLE_TAB_WIDTH = 10
TOP_OFFSET_RATIO = 0.28


def edge_y_position(screen_height: int, window_height: int = WINDOW_HEIGHT) -> int:
    return max(0, round((screen_height - window_height) * TOP_OFFSET_RATIO))


def visible_x_position(screen_width: int, window_width: int = WINDOW_WIDTH) -> int:
    return max(0, screen_width - window_width)


def hidden_x_position(
    screen_width: int,
    visible_tab_width: int = VISIBLE_TAB_WIDTH,
) -> int:
    return max(0, screen_width - visible_tab_width)


class FloatingCountdownWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.label: tk.Label | None = None
        self._hide_after_id: str | None = None
        self._is_visible = False

    def build(self, on_close: Callable[[], None]) -> tk.Label:
        self.root.title("EyeBreak")
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.configure(bg="#14b8a6")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.96)
        self.root.protocol("WM_DELETE_WINDOW", on_close)

        shell = tk.Frame(self.root, bg="#111827", width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        shell.pack(fill=tk.BOTH, expand=True)
        shell.pack_propagate(False)

        tab = tk.Frame(shell, bg="#14b8a6", width=VISIBLE_TAB_WIDTH)
        tab.pack(side=tk.LEFT, fill=tk.Y)

        content = tk.Frame(shell, bg="#111827")
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title = tk.Label(
            content,
            text="下次护眼提醒",
            font=("Microsoft YaHei UI", 9),
            bg="#111827",
            fg="#a7f3d0",
        )
        title.pack(pady=(7, 0))

        self.label = tk.Label(
            content,
            text="--:--",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg="#111827",
            fg="#f9fafb",
        )
        self.label.pack(pady=(0, 6))

        self.root.bind("<Enter>", self.show)
        self.root.bind("<Leave>", self.schedule_hide)
        self.hide()
        return self.label

    def show(self, _event: tk.Event | None = None) -> None:
        self._cancel_scheduled_hide()
        self._move_to_edge(visible=True)

    def schedule_hide(self, _event: tk.Event | None = None) -> None:
        self._cancel_scheduled_hide()
        self._hide_after_id = self.root.after(700, self._hide_if_pointer_outside)

    def hide(self) -> None:
        self._cancel_scheduled_hide()
        self._move_to_edge(visible=False)

    def _hide_if_pointer_outside(self) -> None:
        self._hide_after_id = None
        pointer_x = self.root.winfo_pointerx()
        pointer_y = self.root.winfo_pointery()
        window_x = self.root.winfo_rootx()
        window_y = self.root.winfo_rooty()
        if (
            window_x <= pointer_x < window_x + WINDOW_WIDTH
            and window_y <= pointer_y < window_y + WINDOW_HEIGHT
        ):
            return
        self.hide()

    def _move_to_edge(self, visible: bool) -> None:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = visible_x_position(screen_width) if visible else hidden_x_position(screen_width)
        y = edge_y_position(screen_height)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self._is_visible = visible

    def _cancel_scheduled_hide(self) -> None:
        if not self._hide_after_id:
            return
        self.root.after_cancel(self._hide_after_id)
        self._hide_after_id = None
