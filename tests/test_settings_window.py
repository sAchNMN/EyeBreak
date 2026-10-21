from unittest.mock import MagicMock, patch

from app.stats import UsageStats, format_completion_rate


def test_statistics_completion_rate_display_uses_no_data_for_zero() -> None:
    assert format_completion_rate(UsageStats()) == "暂无数据"
    assert format_completion_rate(
        UsageStats(reminder_count=4, completed_count=3)
    ) == "75%"


@patch("app.settings_window.messagebox.askyesno", return_value=True)
def test_reset_statistics_requires_confirmation_and_calls_reset(mock_confirm) -> None:
    from app.settings_window import SettingsWindow

    window = SettingsWindow.__new__(SettingsWindow)
    window.root = MagicMock()
    window.stats = UsageStats(reminder_count=1)
    window.on_reset_stats = MagicMock()
    window._stats_labels = {}

    window._reset_stats()

    mock_confirm.assert_called_once()
    window.on_reset_stats.assert_called_once_with()
    assert window.stats == UsageStats()
