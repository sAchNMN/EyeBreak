from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Literal


HORIZONTAL_WINDOW_WIDTH = 96
VERTICAL_WINDOW_WIDTH = 144
HORIZONTAL_WINDOW_HEIGHT = 84
VERTICAL_WINDOW_HEIGHT = 72
WINDOW_WIDTH = VERTICAL_WINDOW_WIDTH
WINDOW_HEIGHT = HORIZONTAL_WINDOW_HEIGHT
VISIBLE_TAB_WIDTH = 16
VISIBLE_TAB_HEIGHT = 10
TOP_OFFSET_RATIO = 0.28
EDGE_SNAP_DISTANCE = 12
HIDE_DELAY_MS = 200

DockEdge = Literal["left", "right", "top", "bottom"]


def window_width_for_edge(edge: DockEdge | None) -> int:
    if edge in ("top", "bottom"):
        return HORIZONTAL_WINDOW_WIDTH
    return VERTICAL_WINDOW_WIDTH


def window_height_for_edge(edge: DockEdge | None) -> int:
    if edge in ("top", "bottom"):
        return HORIZONTAL_WINDOW_HEIGHT
    return VERTICAL_WINDOW_HEIGHT


def edge_y_position(screen_height: int, window_height: int = WINDOW_HEIGHT) -> int:
    return max(0, round((screen_height - window_height) * TOP_OFFSET_RATIO))


def visible_x_position(screen_width: int, window_width: int = WINDOW_WIDTH) -> int:
    return max(0, screen_width - window_width)


def hidden_x_position(
    screen_width: int,
    visible_tab_width: int = VISIBLE_TAB_WIDTH,
) -> int:
    return max(0, screen_width - visible_tab_width)


def clamp_position(
    x: int,
    y: int,
    screen_width: int,
    screen_height: int,
    window_width: int = WINDOW_WIDTH,
    window_height: int = WINDOW_HEIGHT,
) -> tuple[int, int]:
    max_x = max(0, screen_width - window_width)
    max_y = max(0, screen_height - window_height)
    return max(0, min(max_x, x)), max(0, min(max_y, y))


def nearest_docked_edge(
    x: int,
    y: int,
    screen_width: int,
    screen_height: int,
    snap_distance: int = EDGE_SNAP_DISTANCE,
    *,
    window_width: int = WINDOW_WIDTH,
    window_height: int = WINDOW_HEIGHT,
) -> DockEdge | None:
    distances: dict[DockEdge, int] = {
        "left": x,
        "right": screen_width - (x + window_width),
        "top": y,
        "bottom": screen_height - (y + window_height),
    }
    edge, distance = min(distances.items(), key=lambda item: item[1])
    if distance <= snap_distance:
        return edge
    return None


def visible_position_for_edge(
    edge: DockEdge,
    x: int,
    y: int,
    screen_width: int,
    screen_height: int,
    *,
    window_width: int = WINDOW_WIDTH,
    window_height: int = WINDOW_HEIGHT,
) -> tuple[int, int]:
    x, y = clamp_position(
        x,
        y,
        screen_width,
        screen_height,
        window_width,
        window_height,
    )
    if edge == "left":
        return 0, y
    if edge == "right":
        return max(0, screen_width - window_width), y
    if edge == "top":
        return x, 0
    return x, max(0, screen_height - window_height)


def hidden_position_for_edge(
    edge: DockEdge,
    x: int,
    y: int,
    screen_width: int,
    screen_height: int,
    *,
    window_width: int = WINDOW_WIDTH,
    window_height: int = WINDOW_HEIGHT,
) -> tuple[int, int]:
    visible_x, visible_y = visible_position_for_edge(
        edge,
        x,
        y,
        screen_width,
        screen_height,
        window_width=window_width,
        window_height=window_height,
    )
    if edge == "left":
        return -(window_width - VISIBLE_TAB_WIDTH), visible_y
    if edge == "right":
        return max(0, screen_width - VISIBLE_TAB_WIDTH), visible_y
    if edge == "top":
        return visible_x, -(window_height - VISIBLE_TAB_HEIGHT)
    return visible_x, max(0, screen_height - VISIBLE_TAB_HEIGHT)


class FloatingCountdownWindow:
    def __init__(
        self,
        root: tk.Tk,
        initial_edge: DockEdge | None = "right",
        initial_x: int = 0,
        initial_y: int | None = None,
    ) -> None:
        self.root = root
        self.label: tk.Label | None = None
        self.status_label: tk.Label | None = None
        self._shell: tk.Frame | None = None
        self._tab: tk.Frame | None = None
        self._content: tk.Frame | None = None
        self._edge = initial_edge
        self._window_width = window_width_for_edge(initial_edge)
        self._window_height = window_height_for_edge(initial_edge)
        self._visible_x = initial_x
        self._visible_y = 0 if initial_y is None else initial_y
        self._initial_y = initial_y
        self._drag_offset_x = 0
        self._drag_offset_y = 0
        self._is_enabled = True
        self._is_hidden = True
        self._is_dragging = False
        self._hide_job: str | None = None
        self._on_show: Callable[[], None] | None = None

    def build(
        self,
        on_close: Callable[[], None],
        on_show: Callable[[], None] | None = None,
    ) -> tk.Label:
        self._on_show = on_show
        self.root.title("EyeBreak")
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.configure(bg="#14b8a6")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.96)
        self.root.protocol("WM_DELETE_WINDOW", on_close)

        self._shell = tk.Frame(
            self.root,
            bg="#111827",
            width=self._window_width,
            height=self._window_height,
        )
        self._shell.pack(fill=tk.BOTH, expand=True)
        self._shell.pack_propagate(False)

        self._tab = tk.Frame(self._shell, bg="#14b8a6")
        self._content = tk.Frame(self._shell, bg="#111827")
        self._place_tab_for_edge()

        self.status_label = tk.Label(
            self._content,
            text="下次护眼提醒",
            font=("Microsoft YaHei UI", 9),
            bg="#111827",
            fg="#a7f3d0",
        )
        self.status_label.pack(pady=(4, 0))

        self.label = tk.Label(
            self._content,
            text="--:--",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg="#111827",
            fg="#f9fafb",
        )
        self.label.pack(pady=(0, 4))

        self._bind_window_events(self.root)
        self._apply_initial_position()
        return self.label

    def set_enabled(self, is_enabled: bool) -> None:
        self._is_enabled = is_enabled
        if not is_enabled:
            self._cancel_hide()
            self._is_dragging = False
            self._is_hidden = True
            self.root.withdraw()
            return

        self.root.deiconify()
        self.show()
        self.schedule_hide()
    def set_paused(self, is_paused: bool) -> None:
        if not self.status_label:
            return
        if is_paused:
            self.status_label.configure(text="暂停中", fg="#fbbf24")
            return
        self.status_label.configure(text="下次护眼提醒", fg="#a7f3d0")

    def set_idle(self, is_idle: bool) -> None:
        if not self.status_label:
            return
        if is_idle:
            self.status_label.configure(text="已离开", fg="#9ca3af")
            return
        self.status_label.configure(text="下次护眼提醒", fg="#a7f3d0")

    def set_fullscreen(self, is_fullscreen: bool) -> None:
        if not self.status_label:
            return
        if is_fullscreen:
            self.status_label.configure(text="全屏中", fg="#60a5fa")
            return
        self.status_label.configure(text="下次护眼提醒", fg="#a7f3d0")

    def show(self, _event: tk.Event | None = None) -> None:
        self._cancel_hide()
        if not self._is_enabled:
            return
        self.root.deiconify()
        if self._edge:
            self._place_tab_for_edge()
            self._move_to_position(*self._visible_position())
        self._is_hidden = False
        if self._on_show:
            self._on_show()

    def schedule_hide(self, _event: tk.Event | None = None) -> None:
        if self._edge and self._is_enabled and not self._is_dragging:
            self._cancel_hide()
            self._hide_job = self.root.after(HIDE_DELAY_MS, self._hide_if_pointer_outside)

    def hide(self) -> None:
        self._cancel_hide()
        if not self._is_enabled:
            return
        if self._edge:
            self._place_tab_for_edge()
            self._move_to_position(*self._hidden_position())
            self._is_hidden = True

    def should_update_display(self) -> bool:
        return self._is_enabled and not self._is_hidden

    def placement(self) -> tuple[DockEdge | None, int, int]:
        return self._edge, self._visible_x, self._visible_y

    def _start_drag(self, event: tk.Event) -> None:
        if not self._is_enabled:
            return
        self._cancel_hide()
        self._is_dragging = True
        self.show()
        self._drag_offset_x = event.x_root - self.root.winfo_rootx()
        self._drag_offset_y = event.y_root - self.root.winfo_rooty()

    def _drag(self, event: tk.Event) -> None:
        if not self._is_enabled:
            return
        self._edge = None
        self._is_hidden = False
        self._place_tab_for_edge()
        x = event.x_root - self._drag_offset_x
        y = event.y_root - self._drag_offset_y
        x, y = clamp_position(
            x,
            y,
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
            self._current_window_width(),
            self._current_window_height(),
        )
        self._move_to_position(x, y)

    def _finish_drag(self, _event: tk.Event) -> None:
        if not self._is_enabled:
            return
        self._cancel_hide()
        self._is_dragging = False
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        if _event is None:
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
        else:
            x = _event.x_root - self._drag_offset_x
            y = _event.y_root - self._drag_offset_y
        x, y = clamp_position(
            x,
            y,
            screen_width,
            screen_height,
            self._current_window_width(),
            self._current_window_height(),
        )
        edge = nearest_docked_edge(
            x,
            y,
            screen_width,
            screen_height,
            window_width=self._current_window_width(),
            window_height=self._current_window_height(),
        )
        if not edge:
            self._edge = None
            self._place_tab_for_edge()
            self._visible_x, self._visible_y = clamp_position(
                x,
                y,
                screen_width,
                screen_height,
                self._current_window_width(),
                self._current_window_height(),
            )
            self._is_hidden = False
            self._move_to_position(self._visible_x, self._visible_y)
            return

        self._edge = edge
        self._window_width = window_width_for_edge(edge)
        self._window_height = window_height_for_edge(edge)
        self._place_tab_for_edge()
        self._visible_x, self._visible_y = visible_position_for_edge(
            edge,
            x,
            y,
            screen_width,
            screen_height,
            window_width=self._window_width,
            window_height=self._window_height,
        )
        self._is_hidden = False
        self._move_to_position(self._visible_x, self._visible_y)

    def _hide_if_pointer_outside(self) -> None:
        self._hide_job = None
        if not self._edge or not self._is_enabled or self._is_dragging:
            return
        pointer_x = self.root.winfo_pointerx()
        pointer_y = self.root.winfo_pointery()
        window_x = self.root.winfo_rootx()
        window_y = self.root.winfo_rooty()
        window_width = self._current_window_width()
        window_height = self._current_window_height()
        if (
            window_x <= pointer_x < window_x + window_width
            and window_y <= pointer_y < window_y + window_height
        ):
            return
        self.hide()

    def _cancel_hide(self) -> None:
        if self._hide_job is None:
            return
        self.root.after_cancel(self._hide_job)
        self._hide_job = None

    def _visible_position(self) -> tuple[int, int]:
        if not self._edge:
            return self._visible_x, self._visible_y
        return visible_position_for_edge(
            self._edge,
            self._visible_x,
            self._visible_y,
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
            window_width=self._current_window_width(),
            window_height=self._current_window_height(),
        )

    def _hidden_position(self) -> tuple[int, int]:
        if not self._edge:
            return self._visible_x, self._visible_y
        return hidden_position_for_edge(
            self._edge,
            self._visible_x,
            self._visible_y,
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
            window_width=self._current_window_width(),
            window_height=self._current_window_height(),
        )

    def _apply_initial_position(self) -> None:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        if self._initial_y is None:
            self._visible_y = edge_y_position(screen_height, self._current_window_height())

        if self._edge:
            self._visible_x, self._visible_y = visible_position_for_edge(
                self._edge,
                self._visible_x,
                self._visible_y,
                screen_width,
                screen_height,
                window_width=self._current_window_width(),
                window_height=self._current_window_height(),
            )
            self._move_to_position(self._visible_x, self._visible_y)
            self._is_hidden = False
            return

        self._visible_x, self._visible_y = clamp_position(
            self._visible_x,
            self._visible_y,
            screen_width,
            screen_height,
            self._current_window_width(),
            self._current_window_height(),
        )
        self._place_tab_for_edge()
        self._move_to_position(self._visible_x, self._visible_y)
        self._is_hidden = False
    def _current_window_width(self) -> int:
        return getattr(self, "_window_width", window_width_for_edge(self._edge))

    def _current_window_height(self) -> int:
        return getattr(self, "_window_height", window_height_for_edge(self._edge))

    def _place_tab_for_edge(self) -> None:
        if not self._tab or not self._content:
            return

        self._tab.place_forget()
        self._content.place_forget()
        edge = self._edge or "right"
        window_width = self._current_window_width()
        window_height = self._current_window_height()
        if edge == "left":
            self._content.place(x=0, y=0, width=window_width - VISIBLE_TAB_WIDTH, height=window_height)
            self._tab.place(x=window_width - VISIBLE_TAB_WIDTH, y=0, width=VISIBLE_TAB_WIDTH, height=window_height)
            return
        if edge == "top":
            self._content.place(x=0, y=0, width=window_width, height=window_height - VISIBLE_TAB_HEIGHT)
            self._tab.place(x=0, y=window_height - VISIBLE_TAB_HEIGHT, width=window_width, height=VISIBLE_TAB_HEIGHT)
            return
        if edge == "bottom":
            self._tab.place(x=0, y=0, width=window_width, height=VISIBLE_TAB_HEIGHT)
            self._content.place(x=0, y=VISIBLE_TAB_HEIGHT, width=window_width, height=window_height - VISIBLE_TAB_HEIGHT)
            return

        self._tab.place(x=0, y=0, width=VISIBLE_TAB_WIDTH, height=window_height)
        self._content.place(x=VISIBLE_TAB_WIDTH, y=0, width=window_width - VISIBLE_TAB_WIDTH, height=window_height)

    def _move_to_position(self, x: int, y: int) -> None:
        self.root.geometry(f"{self._current_window_width()}x{self._current_window_height()}+{x}+{y}")

    def _bind_window_events(self, widget: tk.Widget) -> None:
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.schedule_hide)
        widget.bind("<ButtonPress-1>", self._start_drag)
        widget.bind("<B1-Motion>", self._drag)
        widget.bind("<ButtonRelease-1>", self._finish_drag)
        for child in widget.winfo_children():
            self._bind_window_events(child)
