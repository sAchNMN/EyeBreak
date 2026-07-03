from app.icons import create_icon_image
from app.tray import (
    PAUSE_OPTIONS_MINUTES,
    _format_pause_label,
    _pause_menu,
    _toggle_floating_action,
)


def test_create_icon_image_has_expected_shape() -> None:
    image = create_icon_image()

    assert image.size == (64, 64)
    assert image.mode == "RGBA"


def test_pause_options_cover_short_and_long_breaks() -> None:
    assert PAUSE_OPTIONS_MINUTES == (5, 15, 30, 60, 120)


def test_format_pause_label_uses_minutes_and_hours() -> None:
    assert _format_pause_label(15) == "15分钟"
    assert _format_pause_label(60) == "1小时"
    assert _format_pause_label(120) == "2小时"


def test_pause_menu_actions_pass_selected_minutes() -> None:
    selected_minutes: list[int] = []
    menu = _pause_menu(selected_minutes.append)

    for item in menu:
        item(None)

    assert selected_minutes == list(PAUSE_OPTIONS_MINUTES)


def test_toggle_floating_action_calls_callback() -> None:
    calls: list[bool] = []
    action = _toggle_floating_action(lambda: calls.append(True))

    action(None, None)

    assert calls == [True]