from app.floating_countdown import (
    VISIBLE_TAB_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    edge_y_position,
    hidden_x_position,
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