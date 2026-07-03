import app.timer as timer_module
from app.config import AppConfig
from app.state import AppState
from app.timer import ReminderTimer, format_seconds


def test_format_seconds_rounds_up_remaining_time() -> None:
    assert format_seconds(59.1) == "01:00"
    assert format_seconds(60) == "01:00"
    assert format_seconds(61) == "01:01"


def test_format_seconds_clamps_negative_time() -> None:
    assert format_seconds(-1) == "00:00"


def test_timer_uses_floating_countdown_window() -> None:
    timer = ReminderTimer(AppConfig(), AppState())

    assert timer.countdown_window is None
    assert timer_module.FloatingCountdownWindow.__name__ == "FloatingCountdownWindow"