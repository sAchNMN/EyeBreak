from app.floating_countdown import (
    VISIBLE_TAB_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    clamp_position,
    edge_y_position,
    hidden_position_for_edge,
    hidden_x_position,
    nearest_docked_edge,
    visible_position_for_edge,
    visible_x_position,
)


def test_visible_position_docks_window_to_right_edge() -> None:
    assert visible_x_position(1920) == 1920 - WINDOW_WIDTH


def test_hidden_position_leaves_only_tab_visible() -> None:
    assert hidden_x_position(1920) == 1920 - VISIBLE_TAB_WIDTH


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
        -(WINDOW_HEIGHT - VISIBLE_TAB_WIDTH),
    )
    assert hidden_position_for_edge("bottom", 50, 0, 1920, 1080) == (
        50,
        1080 - VISIBLE_TAB_WIDTH,
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
        {"x": 0, "y": 0, "width": VISIBLE_TAB_WIDTH, "height": WINDOW_HEIGHT},
    )

    tab.calls.clear()
    content.calls.clear()
    window._edge = "left"
    window._place_tab_for_edge()
    assert tab.calls[-1] == (
        "place",
        {
            "x": WINDOW_WIDTH - VISIBLE_TAB_WIDTH,
            "y": 0,
            "width": VISIBLE_TAB_WIDTH,
            "height": WINDOW_HEIGHT,
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
            "y": WINDOW_HEIGHT - VISIBLE_TAB_WIDTH,
            "width": WINDOW_WIDTH,
            "height": VISIBLE_TAB_WIDTH,
        },
    )

    tab.calls.clear()
    content.calls.clear()
    window._edge = "bottom"
    window._place_tab_for_edge()
    assert tab.calls[1] == (
        "place",
        {"x": 0, "y": 0, "width": WINDOW_WIDTH, "height": VISIBLE_TAB_WIDTH},
    )

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
    window._move_to_position.assert_called_once_with(1920 - WINDOW_WIDTH, edge_y_position(1080))