"""Tests for app.platform.protocols — verify Protocol interfaces.

These tests ensure the Protocol definitions are runtime-checkable
and that simple fake implementations satisfy them.
"""

from app.platform.protocols import (
    AutostartManager,
    ConfigRepository,
    FullscreenDetector,
    IdleDetector,
    StateRepository,
)


# ── Fake implementations ────────────────────────────────────────


class FakeIdleDetector:
    def __init__(self, idle_seconds: float = 0.0) -> None:
        self._idle = idle_seconds

    def get_idle_seconds(self) -> float:
        return self._idle


class FakeFullscreenDetector:
    def __init__(self, is_fullscreen: bool = False) -> None:
        self._fullscreen = is_fullscreen

    def is_foreground_fullscreen(self) -> bool:
        return self._fullscreen


class FakeAutostartManager:
    def __init__(self, enabled: bool = False) -> None:
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled


class FakeConfigRepository:
    def __init__(self, config=None) -> None:
        self._config = config
        self.saved: list = []

    def load(self):
        return self._config

    def save(self, config) -> None:
        self.saved.append(config)


class FakeStateRepository:
    def __init__(self, state=None) -> None:
        self._state = state
        self.saved: list = []

    def load(self):
        return self._state

    def save(self, state) -> None:
        self.saved.append(state)


# ── Protocol isinstance checks ──────────────────────────────────


def test_fake_idle_detector_satisfies_protocol() -> None:
    detector = FakeIdleDetector(idle_seconds=42.0)
    assert isinstance(detector, IdleDetector)
    assert detector.get_idle_seconds() == 42.0


def test_fake_fullscreen_detector_satisfies_protocol() -> None:
    detector = FakeFullscreenDetector(is_fullscreen=True)
    assert isinstance(detector, FullscreenDetector)
    assert detector.is_foreground_fullscreen() is True


def test_fake_autostart_manager_satisfies_protocol() -> None:
    manager = FakeAutostartManager(enabled=False)
    assert isinstance(manager, AutostartManager)
    manager.set_enabled(True)
    assert manager.is_enabled() is True


def test_fake_config_repository_satisfies_protocol() -> None:
    repo = FakeConfigRepository(config={"interval": 25})
    assert isinstance(repo, ConfigRepository)
    assert repo.load() == {"interval": 25}
    repo.save({"interval": 10})
    assert repo.saved == [{"interval": 10}]


def test_fake_state_repository_satisfies_protocol() -> None:
    repo = FakeStateRepository(state={"floating": True})
    assert isinstance(repo, StateRepository)
    assert repo.load() == {"floating": True}
    repo.save({"floating": False})
    assert repo.saved == [{"floating": False}]


# ── Existing implementations satisfy protocols ──────────────────


def test_real_idle_detector_satisfies_protocol() -> None:
    from app.idle import get_idle_seconds

    # The module-level function can be wrapped in a simple adapter.
    class IdleAdapter:
        def get_idle_seconds(self) -> float:
            return get_idle_seconds()

    assert isinstance(IdleAdapter(), IdleDetector)


def test_real_fullscreen_detector_satisfies_protocol() -> None:
    from app.fullscreen import is_foreground_window_fullscreen

    class FullscreenAdapter:
        def is_foreground_fullscreen(self) -> bool:
            return is_foreground_window_fullscreen()

    assert isinstance(FullscreenAdapter(), FullscreenDetector)


def test_real_autostart_manager_satisfies_protocol() -> None:
    from app.autostart import is_autostart_enabled, set_autostart

    class AutostartAdapter:
        def is_enabled(self) -> bool:
            return is_autostart_enabled()

        def set_enabled(self, enabled: bool) -> None:
            set_autostart(enabled)

    assert isinstance(AutostartAdapter(), AutostartManager)
