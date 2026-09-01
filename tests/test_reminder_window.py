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
