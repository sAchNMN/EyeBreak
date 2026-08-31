import sys

from app.fullscreen import Rect, is_foreground_window_fullscreen, window_covers_monitor


def test_window_covers_monitor_when_edges_match() -> None:
    assert window_covers_monitor(Rect(0, 0, 1920, 1080), Rect(0, 0, 1920, 1080))


def test_window_covers_monitor_allows_small_tolerance() -> None:
    assert window_covers_monitor(Rect(1, 1, 1919, 1079), Rect(0, 0, 1920, 1080))


def test_window_covers_monitor_rejects_normal_window() -> None:
    assert not window_covers_monitor(Rect(100, 100, 1200, 900), Rect(0, 0, 1920, 1080))


def test_is_foreground_window_fullscreen_returns_false_outside_windows(monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "linux")

    assert is_foreground_window_fullscreen() is False


def test_fullscreen_detector_reuses_win32_api_cache() -> None:
    if sys.platform != "win32":
        return  # skip on non-Windows; no API available

    import app.fullscreen as fullscreen

    fullscreen._get_win32_api.cache_clear()
    first = fullscreen._get_win32_api()
    second = fullscreen._get_win32_api()

    assert first is second
