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


def test_save_applies_config_without_closing_the_window() -> None:
    from app.config import AppConfig
    from app.settings_window import SettingsWindow

    window = SettingsWindow.__new__(SettingsWindow)
    window.root = MagicMock()
    window.config = AppConfig()
    window.entries = {
        "reminder_interval_minutes": MagicMock(get=lambda: "15"),
        "break_duration_seconds": MagicMock(get=lambda: "20"),
        "pause_minutes": MagicMock(get=lambda: "30"),
        "idle_threshold_minutes": MagicMock(get=lambda: "5"),
        "floating_window_scale": MagicMock(get=lambda: "120"),
        "floating_tab_width": MagicMock(get=lambda: "24"),
    }
    window.fullscreen_detection_enabled = MagicMock(get=lambda: True)
    window.floating_tab_color = MagicMock(get=lambda: "#3366ff")
    window.floating_animation_enabled = MagicMock(get=lambda: False)
    window.on_save = MagicMock()
    window._close = MagicMock()

    window._save()

    window.on_save.assert_called_once()
    saved = window.on_save.call_args.args[0]
    assert saved.reminder_interval_minutes == 15
    assert saved.floating_window_scale == 120
    assert saved.floating_tab_width == 24
    assert saved.floating_tab_color == "#3366ff"
    assert saved.floating_animation_enabled is False
    assert window.config is saved
    window._close.assert_not_called()
