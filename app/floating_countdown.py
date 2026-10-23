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
SLIDE_ANIMATION_DURATION_MS = 180
SLIDE_ANIMATION_FRAME_MS = 15
DEFAULT_TAB_COLOR = "#14b8a6"
DEFAULT_WINDOW_SCALE = 100

DockEdge = Literal["left", "right", "top", "bottom"]


def ease_out_cubic(progress: float) -> float:
    """Map linear 0..1 progress onto a decelerating 0..1 curve."""
    clamped = min(1.0, max(0.0, progress))
    return 1.0 - (1.0 - clamped) ** 3


def interpolate_position(
    start: tuple[int, int],
    end: tuple[int, int],
    progress: float,
) -> tuple[int, int]:
    """Return the eased position between two window positions."""
    eased = ease_out_cubic(progress)
    return (
        round(start[0] + (end[0] - start[0]) * eased),
        round(start[1] + (end[1] - start[1]) * eased),
    )


def window_width_for_edge(
    edge: DockEdge | None,
    *,
    scale: float = 1.0,
    tab_width: int = VISIBLE_TAB_WIDTH,
) -> int:
    if edge in ("top", "bottom"):
        return max(1, round(HORIZONTAL_WINDOW_WIDTH * scale))
    content_width = max(
        1,
        round((VERTICAL_WINDOW_WIDTH - VISIBLE_TAB_WIDTH) * scale),
    )
    return content_width + max(1, tab_width)


def tab_thickness_for_edge(
    edge: DockEdge | None,
    tab_width: int = VISIBLE_TAB_WIDTH,
) -> int:
    if edge in ("top", "bottom"):
        return max(3, round(tab_width * VISIBLE_TAB_HEIGHT / VISIBLE_TAB_WIDTH))
    return max(1, tab_width)


def window_height_for_edge(
    edge: DockEdge | None,
    *,
    scale: float = 1.0,
    tab_width: int = VISIBLE_TAB_WIDTH,
) -> int:
    if edge in ("top", "bottom"):
        content_height = max(
            1,
            round((HORIZONTAL_WINDOW_HEIGHT - VISIBLE_TAB_HEIGHT) * scale),
        )
        return content_height + tab_thickness_for_edge(edge, tab_width)
    return max(1, round(VERTICAL_WINDOW_HEIGHT * scale))


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
    visible_tab_width: int = VISIBLE_TAB_WIDTH,
    visible_tab_height: int = VISIBLE_TAB_HEIGHT,
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
        return -(window_width - visible_tab_width), visible_y
    if edge == "right":
        return max(0, screen_width - visible_tab_width), visible_y
    if edge == "top":
        return visible_x, -(window_height - visible_tab_height)
    return visible_x, max(0, screen_height - visible_tab_height)


class FloatingCountdownWindow:
    def __init__(
        self,
        root: tk.Tk,
        initial_edge: DockEdge | None = "right",
        initial_x: int = 0,
        initial_y: int | None = None,
        *,
        window_scale: int = DEFAULT_WINDOW_SCALE,
        tab_width: int = VISIBLE_TAB_WIDTH,
        tab_color: str = DEFAULT_TAB_COLOR,
        animation_enabled: bool = True,
    ) -> None:
        self.root = root
        self.label: tk.Label | None = None
        self.status_label: tk.Label | None = None
        self._shell: tk.Frame | None = None
        self._tab: tk.Frame | None = None
        self._content: tk.Frame | None = None
        self._scale_percent = window_scale
        self._tab_width = tab_width
        self._tab_color = tab_color
        self._animation_enabled = animation_enabled
        self._edge = initial_edge
        self._window_width = window_width_for_edge(
            initial_edge,
            scale=self._scale_factor(),
            tab_width=tab_width,
        )
        self._window_height = window_height_for_edge(
            initial_edge,
            scale=self._scale_factor(),
            tab_width=tab_width,
        )
        self._visible_x = initial_x
        self._visible_y = 0 if initial_y is None else initial_y
        self._initial_y = initial_y
        self._drag_offset_x = 0
        self._drag_offset_y = 0
        self._is_enabled = True
        self._is_hidden = True
        self._is_dragging = False
        self._hide_job: str | None = None
        self._slide_animation_job: str | None = None
        self._slide_animation_start = (0, 0)
        self._slide_animation_end = (0, 0)
        self._slide_animation_elapsed = 0
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
        self.root.configure(bg=self._current_tab_color())
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

        self._tab = tk.Frame(self._shell, bg=self._current_tab_color())
        self._content = tk.Frame(self._shell, bg="#111827")
        self._place_tab_for_edge()

        self.status_label = tk.Label(
            self._content,
            text="下次护眼提醒",
            font=("Microsoft YaHei UI", self._scaled_font_size(9, 7)),
            bg="#111827",
            fg="#a7f3d0",
        )
        self.status_label.pack(pady=(self._scaled_padding(4), 0))

        self.label = tk.Label(
            self._content,
            text="--:--",
            font=("Microsoft YaHei UI", self._scaled_font_size(18, 10), "bold"),
            bg="#111827",
            fg="#f9fafb",
        )
        self.label.pack(pady=(0, self._scaled_padding(4)))

        self._bind_window_events(self.root)
        self._apply_initial_position()
        return self.label

    def apply_appearance(
        self,
        *,
        window_scale: int,
        tab_width: int,
        tab_color: str,
        animation_enabled: bool,
    ) -> None:
        """Apply floating-window appearance settings without recreating the window."""
        self._scale_percent = window_scale
        self._tab_width = tab_width
        self._tab_color = tab_color
        self._animation_enabled = animation_enabled
        if not self._shell:
            return

        self._cancel_slide_animation()
        self.root.configure(bg=tab_color)
        self._tab.configure(bg=tab_color)
        self._window_width = self._width_for_edge(self._edge)
        self._window_height = self._height_for_edge(self._edge)
        self._shell.configure(
            width=self._window_width,
            height=self._window_height,
        )
        self._apply_widget_appearance()
        self._place_tab_for_edge()
        if self._is_hidden:
            self._move_to_position(*self._hidden_position())
        elif self._edge:
            self._move_to_position(*self._visible_position())
        else:
            self._visible_x, self._visible_y = clamp_position(
                self._visible_x,
                self._visible_y,
                self.root.winfo_screenwidth(),
                self.root.winfo_screenheight(),
                self._window_width,
                self._window_height,
            )
            self._move_to_position(self._visible_x, self._visible_y)

    def _apply_widget_appearance(self) -> None:
        if self.status_label:
            self.status_label.configure(
                font=("Microsoft YaHei UI", self._scaled_font_size(9, 7))
            )
            self.status_label.pack_configure(
                pady=(self._scaled_padding(4), 0)
            )
        if self.label:
            self.label.configure(
                font=("Microsoft YaHei UI", self._scaled_font_size(18, 10), "bold")
            )
            self.label.pack_configure(pady=(0, self._scaled_padding(4)))

    def set_enabled(self, is_enabled: bool) -> None:
        self._is_enabled = is_enabled
        if not is_enabled:
            self._cancel_hide()
            self._cancel_slide_animation()
            self._is_dragging = False
            self._is_hidden = True
            self.root.withdraw()
            return

        self.root.deiconify()
        self.show()
        self.schedule_hide()

    def show(self, _event: tk.Event | None = None) -> None:
        self._cancel_hide()
        if not self._is_enabled:
            return
        self.root.deiconify()
        if self._edge:
            self._place_tab_for_edge()
            target = self._visible_position()
            if self._is_hidden and not self._is_dragging:
                self._start_slide_animation(self._window_position(), target)
            elif self._slide_animation_job is None:
                self._move_to_position(*target)
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
        if not self._edge:
            return
        if self._is_hidden and self._slide_animation_job is not None:
            return
        self._place_tab_for_edge()
        self._is_hidden = True
        self._start_slide_animation(self._window_position(), self._hidden_position())

    def should_update_display(self) -> bool:
        return self._is_enabled and not self._is_hidden

    def placement(self) -> tuple[DockEdge | None, int, int]:
        return self._edge, self._visible_x, self._visible_y

    def _start_drag(self, event: tk.Event) -> None:
        if not self._is_enabled:
            return
        self._cancel_hide()
        self._cancel_slide_animation()
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
        self._window_width = self._width_for_edge(edge)
        self._window_height = self._height_for_edge(edge)
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

    def _window_position(self) -> tuple[int, int]:
        return self.root.winfo_rootx(), self.root.winfo_rooty()

    def _start_slide_animation(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> None:
        self._cancel_slide_animation()
        if start == end or not self._current_animation_enabled():
            self._move_to_position(*end)
            return
        self._slide_animation_start = start
        self._slide_animation_end = end
        self._slide_animation_elapsed = 0
        self._move_to_position(*start)
        self._slide_animation_job = self.root.after(
            SLIDE_ANIMATION_FRAME_MS,
            self._advance_slide_animation,
        )

    def _advance_slide_animation(self) -> None:
        self._slide_animation_job = None
        if not self._is_enabled or self._is_dragging:
            return
        self._slide_animation_elapsed += SLIDE_ANIMATION_FRAME_MS
        progress = self._slide_animation_elapsed / SLIDE_ANIMATION_DURATION_MS
        self._move_to_position(
            *interpolate_position(
                self._slide_animation_start,
                self._slide_animation_end,
                progress,
            )
        )
        if progress < 1.0:
            self._slide_animation_job = self.root.after(
                SLIDE_ANIMATION_FRAME_MS,
                self._advance_slide_animation,
            )

    def _cancel_slide_animation(self) -> None:
        if self._slide_animation_job is None:
            return
        self.root.after_cancel(self._slide_animation_job)
        self._slide_animation_job = None

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
            visible_tab_width=self._current_tab_width(),
            visible_tab_height=self._tab_thickness(),
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

    def _scale_factor(self) -> float:
        return max(
            0.1,
            getattr(self, "_scale_percent", DEFAULT_WINDOW_SCALE) / 100.0,
        )

    def _current_tab_width(self) -> int:
        return getattr(self, "_tab_width", VISIBLE_TAB_WIDTH)

    def _current_tab_color(self) -> str:
        return getattr(self, "_tab_color", DEFAULT_TAB_COLOR)

    def _current_animation_enabled(self) -> bool:
        return getattr(self, "_animation_enabled", True)

    def _scaled_font_size(self, base: int, minimum: int) -> int:
        return max(minimum, round(base * self._scale_factor()))

    def _scaled_padding(self, value: int) -> int:
        return max(1, round(value * self._scale_factor()))

    def _width_for_edge(self, edge: DockEdge | None) -> int:
        return window_width_for_edge(
            edge,
            scale=self._scale_factor(),
            tab_width=self._current_tab_width(),
        )

    def _height_for_edge(self, edge: DockEdge | None) -> int:
        return window_height_for_edge(
            edge,
            scale=self._scale_factor(),
            tab_width=self._current_tab_width(),
        )

    def _tab_thickness(self) -> int:
        return tab_thickness_for_edge(self._edge, self._current_tab_width())

    def _current_window_width(self) -> int:
        return getattr(self, "_window_width", self._width_for_edge(self._edge))

    def _current_window_height(self) -> int:
        return getattr(self, "_window_height", self._height_for_edge(self._edge))

    def _place_tab_for_edge(self) -> None:
        if not self._tab or not self._content:
            return

        self._tab.place_forget()
        self._content.place_forget()
        edge = self._edge or "right"
        window_width = self._current_window_width()
        window_height = self._current_window_height()
        tab = self._tab_thickness()
        if edge == "left":
            self._content.place(x=0, y=0, width=window_width - tab, height=window_height)
            self._tab.place(x=window_width - tab, y=0, width=tab, height=window_height)
            return
        if edge == "top":
            self._content.place(x=0, y=0, width=window_width, height=window_height - tab)
            self._tab.place(x=0, y=window_height - tab, width=window_width, height=tab)
            return
        if edge == "bottom":
            self._tab.place(x=0, y=0, width=window_width, height=tab)
            self._content.place(x=0, y=tab, width=window_width, height=window_height - tab)
            return

        self._tab.place(x=0, y=0, width=tab, height=window_height)
        self._content.place(x=tab, y=0, width=window_width - tab, height=window_height)

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
