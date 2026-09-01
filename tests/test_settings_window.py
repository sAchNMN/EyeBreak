from unittest.mock import MagicMock, patch

import pytest

from app.config import AppConfig
from app.settings_window import parse_settings_values
from app.stats import UsageStats, format_completion_rate


def test_parse_settings_values_returns_config() -> None:
    config = parse_settings_values("15", "20", "30", "0", False)

    assert config == AppConfig(
        reminder_interval_minutes=15,
        break_duration_seconds=20,
        pause_minutes=30,
        idle_threshold_minutes=0,
        fullscreen_detection_enabled=False,
    )


def test_parse_settings_values_allows_decimal_minutes() -> None:
    config = parse_settings_values("0.5", "10", "1.5", "2.5", True)

    assert config.reminder_interval_minutes == 0.5
    assert config.pause_minutes == 1.5
    assert config.idle_threshold_minutes == 2.5
    assert config.fullscreen_detection_enabled is True


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (("0", "20", "30", "5"), "提醒间隔必须大于 0"),
        (("15", "1.5", "30", "5"), "休息时长必须是大于 0 的整数"),
        (("15", "20", "0", "5"), "默认暂停必须大于 0"),
        (("15", "20", "30", "-1"), "离开检测不能小于 0"),
    ],
)
def test_parse_settings_values_rejects_invalid_values(
    values: tuple[str, str, str, str],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        parse_settings_values(*values)


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
