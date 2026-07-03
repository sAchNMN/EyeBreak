from app.timer import format_seconds


def test_format_seconds_rounds_up_remaining_time() -> None:
    assert format_seconds(59.1) == "01:00"
    assert format_seconds(60) == "01:00"
    assert format_seconds(61) == "01:01"


def test_format_seconds_clamps_negative_time() -> None:
    assert format_seconds(-1) == "00:00"