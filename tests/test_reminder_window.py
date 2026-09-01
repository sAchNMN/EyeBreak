from unittest.mock import MagicMock

from app.reminder_window import ReminderWindow


def test_zero_countdown_calls_complete_instead_of_skip() -> None:
    window = ReminderWindow.__new__(ReminderWindow)
    window.remaining_seconds = 0
    window.countdown_label = MagicMock()
    window.root = MagicMock()
    window.on_complete = MagicMock()
    window.on_skip = MagicMock()

    window._tick()

    window.on_complete.assert_called_once_with()
    window.on_skip.assert_not_called()
    window.root.destroy.assert_called_once_with()


def test_pause_buttons_change_pause_by_five_and_clamp_to_bounds() -> None:
    window = ReminderWindow.__new__(ReminderWindow)
    window.pause_minutes = 15
    window.pause_button = MagicMock()

    assert window._increase_pause_minutes() == "break"
    assert window.pause_minutes == 20
    assert window._decrease_pause_minutes() == "break"
    assert window.pause_minutes == 15

    window.pause_minutes = window.MIN_PAUSE_MINUTES
    window._decrease_pause_minutes()
    assert window.pause_minutes == window.MIN_PAUSE_MINUTES

    window.pause_minutes = window.MAX_PAUSE_MINUTES
    window._increase_pause_minutes()
    assert window.pause_minutes == window.MAX_PAUSE_MINUTES


def test_quick_pause_calls_callback_with_selected_minutes_and_closes() -> None:
    window = ReminderWindow.__new__(ReminderWindow)
    window.on_pause = MagicMock()
    window.root = MagicMock()

    for minutes in (5, 15, 30):
        window._pause_for(minutes)

    assert [call.args[0] for call in window.on_pause.call_args_list] == [5, 15, 30]
    assert window.root.destroy.call_count == 3


def test_today_pause_calls_callback_and_closes() -> None:
    window = ReminderWindow.__new__(ReminderWindow)
    window.on_pause_today = MagicMock()
    window.root = MagicMock()

    window._pause_today()

    window.on_pause_today.assert_called_once_with()
    window.root.destroy.assert_called_once_with()
