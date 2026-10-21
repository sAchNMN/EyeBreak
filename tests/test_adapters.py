"""Tests for app.platform.adapters — verify the real adapter classes
satisfy their Protocols and delegate correctly to existing modules.
"""

from __future__ import annotations

from app.platform.adapters import (
    AutostartManagerAdapter,
    FullscreenDetectorAdapter,
    IdleDetectorAdapter,
)
from app.platform.protocols import (
    AutostartManager,
    FullscreenDetector,
    IdleDetector,
)


# ── isinstance checks ────────────────────────────────────────────


def test_idle_detector_adapter_satisfies_protocol() -> None:
    assert isinstance(IdleDetectorAdapter(), IdleDetector)


def test_fullscreen_detector_adapter_satisfies_protocol() -> None:
    assert isinstance(FullscreenDetectorAdapter(), FullscreenDetector)


def test_autostart_manager_adapter_satisfies_protocol() -> None:
    assert isinstance(AutostartManagerAdapter(), AutostartManager)


# ── Delegation checks (smoke — real modules are exercised) ───────


def test_idle_adapter_returns_float() -> None:
    result = IdleDetectorAdapter().get_idle_seconds()
    assert isinstance(result, float)
    assert result >= 0.0


def test_fullscreen_adapter_returns_bool() -> None:
    result = FullscreenDetectorAdapter().is_foreground_fullscreen()
    assert isinstance(result, bool)


def test_autostart_adapter_delegates(monkeypatch) -> None:
    calls: list[bool] = []
    monkeypatch.setattr(
        "app.platform.adapters.is_autostart_enabled", lambda: False
    )
    monkeypatch.setattr(
        "app.platform.adapters.set_autostart", calls.append
    )

    manager = AutostartManagerAdapter()

    assert manager.is_enabled() is False
    manager.set_enabled(True)
    assert calls == [True]