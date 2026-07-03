from app.tray import PAUSE_OPTIONS_MINUTES, _create_icon_image, _format_pause_label


def test_create_icon_image_has_expected_shape() -> None:
    image = _create_icon_image()

    assert image.size == (64, 64)
    assert image.mode == "RGBA"


def test_pause_options_cover_short_and_long_breaks() -> None:
    assert PAUSE_OPTIONS_MINUTES == (5, 15, 30, 60, 120)


def test_format_pause_label_uses_minutes_and_hours() -> None:
    assert _format_pause_label(15) == "15分钟"
    assert _format_pause_label(60) == "1小时"
    assert _format_pause_label(120) == "2小时"