import tkinter as tk

from app.floating_countdown import (
    DEFAULT_TAB_COLOR,
    HORIZONTAL_WINDOW_WIDTH,
    SLIDE_ANIMATION_FRAME_MS,
    VISIBLE_TAB_HEIGHT,
    VISIBLE_TAB_WIDTH,
    VERTICAL_WINDOW_HEIGHT,
    VERTICAL_WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    clamp_position,
    edge_y_position,
    hidden_position_for_edge,
    hidden_x_position,
    interpolate_position,
    nearest_docked_edge,
    tab_thickness_for_edge,
    visible_position_for_edge,
    visible_x_position,
    window_height_for_edge,
    window_width_for_edge,
)


def test_visible_position_docks_window_to_right_edge() -> None:
    assert visible_x_position(1920) == 1920 - WINDOW_WIDTH


def test_hidden_position_leaves_only_tab_visible() -> None:
    assert hidden_x_position(1920) == 1920 - VISIBLE_TAB_WIDTH


def test_docked_tab_has_a_reachable_width() -> None:
    assert VISIBLE_TAB_WIDTH == 16


def test_window_width_follows_docked_edge() -> None:
    assert HORIZONTAL_WINDOW_WIDTH == 96
    assert VERTICAL_WINDOW_WIDTH == 144
    assert WINDOW_WIDTH == VERTICAL_WINDOW_WIDTH
    assert window_width_for_edge("top") == HORIZONTAL_WINDOW_WIDTH
    assert window_width_for_edge("bottom") == HORIZONTAL_WINDOW_WIDTH
    assert window_width_for_edge("left") == VERTICAL_WINDOW_WIDTH
    assert window_width_for_edge("right") == VERTICAL_WINDOW_WIDTH
    assert window_width_for_edge(None) == VERTICAL_WINDOW_WIDTH


def test_top_and_bottom_tabs_are_thinner_than_side_tabs() -> None:
    assert VISIBLE_TAB_HEIGHT == 10
    assert tab_thickness_for_edge("top") == VISIBLE_TAB_HEIGHT


def test_window_scale_scales_content_without_scaling_the_configured_tab() -> None:
    base_content_width = VERTICAL_WINDOW_WIDTH - VISIBLE_TAB_WIDTH
    base_top_content_height = WINDOW_HEIGHT - VISIBLE_TAB_HEIGHT

    assert window_width_for_edge(
        "right", scale=1.5, tab_width=20
    ) == round(base_content_width * 1.5) + 20
    assert window_height_for_edge("right", scale=1.5, tab_width=20) == round(
        VERTICAL_WINDOW_HEIGHT * 1.5
    )
    assert window_height_for_edge("top", scale=1.5, tab_width=20) == (
        round(base_top_content_height * 1.5)
        + tab_thickness_for_edge("top", 20)
    )


def test_tab_width_changes_exposed_strip_without_shrinking_content() -> None:
    narrow_width = window_width_for_edge("right", tab_width=10)
    wide_width = window_width_for_edge("right", tab_width=30)
    assert wide_width - narrow_width == 20

    for tab_width in (6, 16, 40):
        thickness = tab_thickness_for_edge("top", tab_width)
        assert window_height_for_edge("top", tab_width=tab_width) - thickness == (
            WINDOW_HEIGHT - VISIBLE_TAB_HEIGHT
        )


def test_edge_y_position_uses_stable_upper_screen_offset() -> None:
    assert edge_y_position(1080) == round((1080 - WINDOW_HEIGHT) * 0.28)


def test_edge_positions_do_not_go_negative_on_small_screens() -> None:
    assert visible_x_position(1) == 0
    assert hidden_x_position(1) == 0
    assert edge_y_position(1) == 0


def test_clamp_position_keeps_window_inside_screen() -> None:
    assert clamp_position(-10, 9999, 1920, 1080) == (0, 1080 - WINDOW_HEIGHT)


def test_nearest_docked_edge_detects_only_near_edges() -> None:
    assert nearest_docked_edge(5, 100, 1920, 1080) == "left"
    assert nearest_docked_edge(1920 - WINDOW_WIDTH - 5, 100, 1920, 1080) == "right"
    assert nearest_docked_edge(200, 6, 1920, 1080) == "top"
    assert nearest_docked_edge(200, 1080 - WINDOW_HEIGHT - 6, 1920, 1080) == "bottom"
    assert nearest_docked_edge(500, 400, 1920, 1080) is None


def test_visible_position_for_edge_snaps_to_selected_edge() -> None:
    assert visible_position_for_edge("left", 50, 60, 1920, 1080) == (0, 60)
    assert visible_position_for_edge("right", 50, 60, 1920, 1080) == (
        1920 - WINDOW_WIDTH,
        60,
    )
    assert visible_position_for_edge("top", 50, 60, 1920, 1080) == (50, 0)
    assert visible_position_for_edge("bottom", 50, 60, 1920, 1080) == (
        50,
        1080 - WINDOW_HEIGHT,
    )


def test_hidden_position_for_edge_leaves_tab_visible() -> None:
    assert hidden_position_for_edge("left", 0, 60, 1920, 1080) == (
        -(WINDOW_WIDTH - VISIBLE_TAB_WIDTH),
        60,
    )
    assert hidden_position_for_edge("right", 0, 60, 1920, 1080) == (
        1920 - VISIBLE_TAB_WIDTH,
        60,
    )
    assert hidden_position_for_edge("top", 50, 0, 1920, 1080) == (
        50,
        -(WINDOW_HEIGHT - VISIBLE_TAB_HEIGHT),
    )
    assert hidden_position_for_edge("bottom", 50, 0, 1920, 1080) == (
        50,
        1080 - VISIBLE_TAB_HEIGHT,
    )

class FakePanel:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def place_forget(self) -> None:
        self.calls.append(("forget", None))

    def place(self, **kwargs: object) -> None:
        self.calls.append(("place", kwargs))


def test_placement_returns_visible_position_not_hidden_tab_position() -> None:
    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window._edge = "top"
    window._visible_x = 300
    window._visible_y = 0

    assert window.placement() == ("top", 300, 0)


def test_place_tab_for_edge_uses_inside_screen_side() -> None:
    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    tab = FakePanel()
    content = FakePanel()
    window._tab = tab
    window._content = content

    window._edge = "right"
    window._place_tab_for_edge()
    assert tab.calls[-1] == (
        "place",
        {"x": 0, "y": 0, "width": VISIBLE_TAB_WIDTH, "height": 72},
    )

    tab.calls.clear()
    content.calls.clear()
    window._edge = "left"
    window._place_tab_for_edge()
    assert tab.calls[-1] == (
        "place",
        {
            "x": VERTICAL_WINDOW_WIDTH - VISIBLE_TAB_WIDTH,
            "y": 0,
            "width": VISIBLE_TAB_WIDTH,
            "height": 72,
        },
    )

    tab.calls.clear()
    content.calls.clear()
    window._edge = "top"
    window._place_tab_for_edge()
    assert tab.calls[-1] == (
        "place",
        {
            "x": 0,
            "y": WINDOW_HEIGHT - VISIBLE_TAB_HEIGHT,
            "width": HORIZONTAL_WINDOW_WIDTH,
            "height": VISIBLE_TAB_HEIGHT,
        },
    )

    tab.calls.clear()
    content.calls.clear()
    window._edge = "bottom"
    window._place_tab_for_edge()
    assert tab.calls[1] == (
        "place",
        {"x": 0, "y": 0, "width": HORIZONTAL_WINDOW_WIDTH, "height": VISIBLE_TAB_HEIGHT},
    )


def test_edge_layout_uses_directional_window_widths() -> None:
    from app.floating_countdown import FloatingCountdownWindow

    for edge, expected_width in (
        ("left", VERTICAL_WINDOW_WIDTH),
        ("right", VERTICAL_WINDOW_WIDTH),
        ("top", HORIZONTAL_WINDOW_WIDTH),
        ("bottom", HORIZONTAL_WINDOW_WIDTH),
    ):
        window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
        window._tab = FakePanel()
        window._content = FakePanel()
        window._edge = edge

        window._place_tab_for_edge()

        content_call = window._content.calls[-1][1]
        assert content_call["width"] == (
            expected_width - VISIBLE_TAB_WIDTH
            if edge in ("left", "right")
            else expected_width
        )


def test_finish_drag_changes_width_only_after_docking_to_new_edge() -> None:
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window.root.winfo_screenwidth.return_value = 1920
    window.root.winfo_screenheight.return_value = 1080
    window.root.winfo_rootx.return_value = 400
    window.root.winfo_rooty.return_value = 0
    window._edge = None
    window._window_width = VERTICAL_WINDOW_WIDTH
    window._is_enabled = True
    window._is_dragging = True
    window._hide_job = None
    window._place_tab_for_edge = MagicMock()
    window._move_to_position = MagicMock()
    window._visible_x = 400
    window._visible_y = 0

    window._finish_drag(None)

    assert window._edge == "top"
    assert window._window_width == HORIZONTAL_WINDOW_WIDTH
    window._move_to_position.assert_called_once_with(400, 0)


def test_finish_drag_uses_release_position_to_anchor_right_edge() -> None:
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window.root.winfo_screenwidth.return_value = 1920
    window.root.winfo_screenheight.return_value = 1080
    window.root.winfo_rootx.return_value = 400
    window.root.winfo_rooty.return_value = 100
    window._edge = None
    window._window_width = HORIZONTAL_WINDOW_WIDTH
    window._window_height = WINDOW_HEIGHT
    window._is_enabled = True
    window._is_dragging = True
    window._hide_job = None
    window._drag_offset_x = 10
    window._drag_offset_y = 10
    window._place_tab_for_edge = MagicMock()
    window._move_to_position = MagicMock()

    window._finish_drag(SimpleNamespace(x_root=1910, y_root=110))

    assert window._edge == "right"
    assert window._window_width == VERTICAL_WINDOW_WIDTH
    assert window._window_height == 72
    window._move_to_position.assert_called_once_with(1920 - VERTICAL_WINDOW_WIDTH, 100)


def test_initial_docked_window_is_visible() -> None:
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window.root.winfo_screenwidth.return_value = 1920
    window.root.winfo_screenheight.return_value = 1080
    window._initial_y = None
    window._edge = "right"
    window._visible_x = 0
    window._visible_y = 0
    window._is_hidden = True
    window._move_to_position = MagicMock()

    window._apply_initial_position()

    assert window._is_hidden is False
    window._move_to_position.assert_called_once_with(
        1920 - WINDOW_WIDTH,
        edge_y_position(1080, 72),
    )


def test_schedule_hide_uses_a_short_grace_period() -> None:
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window._edge = "right"
    window._is_enabled = True
    window._is_hidden = False
    window._is_dragging = False
    window._hide_job = None
    window.root.after.return_value = "hide-job"

    window.schedule_hide()

    delay, callback = window.root.after.call_args.args
    assert delay == 200
    assert callback == window._hide_if_pointer_outside


def test_show_cancels_pending_hide() -> None:
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window._edge = "right"
    window._is_enabled = True
    window._is_hidden = True
    window._is_dragging = False
    window._hide_job = "hide-job"
    window._slide_animation_job = None
    window._on_show = None
    window._visible_x = 1600
    window._visible_y = 100
    window.root.winfo_screenwidth.return_value = 1920
    window.root.winfo_screenheight.return_value = 1080
    window.root.winfo_rootx.return_value = 1600
    window.root.winfo_rooty.return_value = 100
    window._place_tab_for_edge = MagicMock()
    window._visible_position = MagicMock(return_value=(1, 2))
    window._move_to_position = MagicMock()

    window.show()

    window.root.after_cancel.assert_called_once_with("hide-job")
    assert window._hide_job is None


def test_enabling_docked_window_schedules_initial_hide_check() -> None:
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window.root.after.return_value = "hide-job"
    window._edge = "right"
    window._is_enabled = False
    window._is_hidden = True
    window._is_dragging = False
    window._hide_job = None
    window._slide_animation_job = None
    window._on_show = None
    window._visible_x = 1600
    window._visible_y = 100
    window.root.winfo_screenwidth.return_value = 1920
    window.root.winfo_screenheight.return_value = 1080
    window.root.winfo_rootx.return_value = 1600
    window.root.winfo_rooty.return_value = 100
    window._place_tab_for_edge = MagicMock()
    window._visible_position = MagicMock(return_value=(1, 2))
    window._move_to_position = MagicMock()

    window.set_enabled(True)

    window.root.after.assert_called_with(200, window._hide_if_pointer_outside)
    assert window.root.after.call_count == 2


def test_schedule_hide_does_nothing_while_dragging() -> None:
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window._edge = "right"
    window._is_enabled = True
    window._is_dragging = True
    window._hide_if_pointer_outside = MagicMock()

    window.schedule_hide()

    window._hide_if_pointer_outside.assert_not_called()


def test_disabling_window_resets_drag_state() -> None:
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window._is_enabled = True
    window._is_dragging = True
    window._hide_job = "hide-job"
    window._slide_animation_job = None

    window.set_enabled(False)

    assert window._is_dragging is False


def test_bottom_layout_gives_countdown_text_enough_height() -> None:
    from app.floating_countdown import FloatingCountdownWindow

    root = tk.Tk()
    root.withdraw()
    try:
        window = FloatingCountdownWindow(root, initial_edge="bottom")
        window.build(lambda: None)
        root.update_idletasks()

        assert root.winfo_reqheight() == WINDOW_HEIGHT
        status_bottom = window.status_label.winfo_y() + window.status_label.winfo_height()
        countdown_top = window.label.winfo_y()
        countdown_bottom = countdown_top + window.label.winfo_height()
        content_bottom = window._content.winfo_y() + window._content.winfo_height()

        assert status_bottom <= countdown_top
        assert window.label.winfo_height() >= window.label.winfo_reqheight()
        assert countdown_bottom <= content_bottom
    finally:
        root.destroy()


def test_interpolate_position_starts_and_ends_exactly() -> None:
    assert interpolate_position((10, 20), (110, 80), 0.0) == (10, 20)
    assert interpolate_position((10, 20), (110, 80), 1.0) == (110, 80)


def test_interpolate_position_eases_out_toward_the_target() -> None:
    halfway_x, _ = interpolate_position((0, 0), (100, 0), 0.5)

    assert halfway_x == 88


def _make_docked_window(edge: str = "right"):
    from unittest.mock import MagicMock

    from app.floating_countdown import FloatingCountdownWindow

    window = FloatingCountdownWindow.__new__(FloatingCountdownWindow)
    window.root = MagicMock()
    window.root.winfo_screenwidth.return_value = 1920
    window.root.winfo_screenheight.return_value = 1080
    window.root.after.return_value = "animation-job"
    window._edge = edge
    window._visible_x = 1920 - VERTICAL_WINDOW_WIDTH
    window._visible_y = 200
    window._window_width = VERTICAL_WINDOW_WIDTH
    window._window_height = 72
    window._is_enabled = True
    window._is_hidden = True
    window._is_dragging = False
    window._hide_job = None
    window._slide_animation_job = None
    window._scale_percent = 100
    window._tab_width = VISIBLE_TAB_WIDTH
    window._tab_color = DEFAULT_TAB_COLOR
    window._animation_enabled = True
    window._on_show = None
    window.root.winfo_rootx.return_value = 1920 - VISIBLE_TAB_WIDTH
    window.root.winfo_rooty.return_value = 200
    window._place_tab_for_edge = MagicMock()
    window._move_to_position = MagicMock()
    return window


def test_show_slides_a_docked_window_out_from_its_hidden_tab() -> None:
    window = _make_docked_window()
    hidden = hidden_position_for_edge(
        "right",
        window._visible_x,
        window._visible_y,
        1920,
        1080,
        window_width=VERTICAL_WINDOW_WIDTH,
        window_height=72,
    )

    window.show()

    window._move_to_position.assert_called_once_with(*hidden)
    assert window._is_hidden is False
    delay, callback = window.root.after.call_args.args
    assert delay == SLIDE_ANIMATION_FRAME_MS
    assert callback == window._advance_slide_animation

    for _ in range(100):
        if window._slide_animation_job is None:
            break
        window._advance_slide_animation()

    assert window._slide_animation_job is None
    window._move_to_position.assert_called_with(
        1920 - VERTICAL_WINDOW_WIDTH,
        200,
    )


def test_show_does_not_restart_animation_while_it_is_running() -> None:
    window = _make_docked_window()
    window.show()
    window.root.after.reset_mock()

    window.show()

    window.root.after.assert_not_called()


def test_show_while_already_visible_does_not_animate() -> None:
    window = _make_docked_window()
    window._is_hidden = False

    window.show()

    assert window._slide_animation_job is None
    window._move_to_position.assert_called_once_with(
        1920 - VERTICAL_WINDOW_WIDTH,
        200,
    )


def test_show_of_an_undocked_window_does_not_animate() -> None:
    window = _make_docked_window()
    window._edge = None
    window._is_hidden = False

    window.show()

    assert window._slide_animation_job is None
    window._move_to_position.assert_not_called()


def test_show_jumps_without_animation_when_transition_is_disabled() -> None:
    window = _make_docked_window()
    window._animation_enabled = False

    window.show()

    assert window._slide_animation_job is None
    window._move_to_position.assert_called_once_with(
        1920 - VERTICAL_WINDOW_WIDTH,
        200,
    )


def test_hide_jumps_without_animation_when_transition_is_disabled() -> None:
    window = _make_docked_window()
    window._is_hidden = False
    window._animation_enabled = False
    window.root.winfo_rootx.return_value = 1920 - VERTICAL_WINDOW_WIDTH
    hidden = hidden_position_for_edge(
        "right",
        window._visible_x,
        window._visible_y,
        1920,
        1080,
        window_width=VERTICAL_WINDOW_WIDTH,
        window_height=72,
    )

    window.hide()

    assert window._slide_animation_job is None
    assert window._is_hidden is True
    window._move_to_position.assert_called_once_with(*hidden)


def test_apply_appearance_updates_size_color_and_animation_flag() -> None:
    from unittest.mock import MagicMock

    window = _make_docked_window()
    window._shell = MagicMock()
    window._tab = MagicMock()
    window.status_label = MagicMock()
    window.label = MagicMock()

    window.apply_appearance(
        window_scale=150,
        tab_width=30,
        tab_color="#ff8800",
        animation_enabled=False,
    )

    expected_width = window_width_for_edge("right", scale=1.5, tab_width=30)
    expected_height = window_height_for_edge("right", scale=1.5, tab_width=30)
    assert window._window_width == expected_width
    assert window._window_height == expected_height
    assert window._animation_enabled is False
    window.root.configure.assert_called_with(bg="#ff8800")
    window._tab.configure.assert_called_with(bg="#ff8800")
    window._shell.configure.assert_called_with(
        width=expected_width,
        height=expected_height,
    )
    window._place_tab_for_edge.assert_called_once()
    window._move_to_position.assert_called_with(1920 - 30, 200)


def test_start_drag_cancels_the_slide_animation_and_snaps_panel_visible() -> None:
    from types import SimpleNamespace

    window = _make_docked_window()
    visible_x = 1920 - VERTICAL_WINDOW_WIDTH
    window.show()
    window.root.winfo_rootx.return_value = visible_x

    window._start_drag(SimpleNamespace(x_root=visible_x + 10, y_root=220))

    window.root.after_cancel.assert_called_with("animation-job")
    assert window._slide_animation_job is None
    assert window._drag_offset_x == 10
    assert window._drag_offset_y == 20
    window._move_to_position.assert_called_with(visible_x, 200)


def test_hide_slides_the_docked_window_back_to_its_tab() -> None:
    window = _make_docked_window()
    window._is_hidden = False
    hidden = hidden_position_for_edge(
        "right",
        window._visible_x,
        window._visible_y,
        1920,
        1080,
        window_width=VERTICAL_WINDOW_WIDTH,
        window_height=72,
    )
    window.root.winfo_rootx.return_value = 1920 - VERTICAL_WINDOW_WIDTH

    window.hide()

    assert window._is_hidden is True
    window._move_to_position.assert_called_once_with(
        1920 - VERTICAL_WINDOW_WIDTH,
        200,
    )
    delay, callback = window.root.after.call_args.args
    assert delay == SLIDE_ANIMATION_FRAME_MS
    assert callback == window._advance_slide_animation

    for _ in range(100):
        if window._slide_animation_job is None:
            break
        window._advance_slide_animation()

    assert window._slide_animation_job is None
    window._move_to_position.assert_called_with(*hidden)


def test_hide_does_not_restart_while_the_panel_is_already_sliding_away() -> None:
    window = _make_docked_window()
    window._is_hidden = False
    window.root.winfo_rootx.return_value = 1920 - VERTICAL_WINDOW_WIDTH
    window.hide()
    window.root.after.reset_mock()

    window.hide()

    window.root.after.assert_not_called()


def test_show_reverses_an_in_progress_hide_from_the_current_position() -> None:
    window = _make_docked_window()
    window._is_hidden = False
    window.root.winfo_rootx.return_value = 1920 - VERTICAL_WINDOW_WIDTH
    window.hide()
    window.root.winfo_rootx.return_value = 1800

    window.show()

    window.root.after_cancel.assert_called_with("animation-job")
    window._move_to_position.assert_called_with(1800, 200)
    assert window._is_hidden is False


def test_hide_reverses_an_in_progress_show_from_the_current_position() -> None:
    window = _make_docked_window()
    window.show()
    window.root.winfo_rootx.return_value = 1800

    window.hide()

    window.root.after_cancel.assert_called_with("animation-job")
    window._move_to_position.assert_called_with(1800, 200)
    assert window._is_hidden is True


def test_disabling_window_cancels_the_slide_animation() -> None:
    window = _make_docked_window()
    window.show()

    window.set_enabled(False)

    window.root.after_cancel.assert_called_with("animation-job")
    assert window._slide_animation_job is None
    window.root.withdraw.assert_called_once()


def test_real_tk_window_uses_directional_widths() -> None:
    from app.floating_countdown import FloatingCountdownWindow

    for edge, expected_width, expected_height in (
        ("left", VERTICAL_WINDOW_WIDTH, 72),
        ("right", VERTICAL_WINDOW_WIDTH, 72),
        ("top", HORIZONTAL_WINDOW_WIDTH, WINDOW_HEIGHT),
        ("bottom", HORIZONTAL_WINDOW_WIDTH, WINDOW_HEIGHT),
    ):
        root = tk.Tk()
        root.withdraw()
        try:
            window = FloatingCountdownWindow(root, initial_edge=edge)
            window.build(lambda: None)
            root.update_idletasks()

            assert root.winfo_reqwidth() == expected_width
            assert root.winfo_reqheight() == expected_height
        finally:
            root.destroy()
