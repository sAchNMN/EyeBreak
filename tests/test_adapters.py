"""Tests for app.platform.adapters — verify the real adapter classes
satisfy their Protocols and delegate correctly to existing modules.
"""

from __future__ import annotations

from app.platform.adapters import (
    AutostartManagerAdapter,
    ConfigRepositoryAdapter,
    FullscreenDetectorAdapter,
    IdleDetectorAdapter,
    StateRepositoryAdapter,
)
from app.platform.protocols import (
    AutostartManager,
    ConfigRepository,
    FullscreenDetector,
    IdleDetector,
    StateRepository,
)


# ── isinstance checks ────────────────────────────────────────────


def test_idle_detector_adapter_satisfies_protocol() -> None:
    assert isinstance(IdleDetectorAdapter(), IdleDetector)


def test_fullscreen_detector_adapter_satisfies_protocol() -> None:
    assert isinstance(FullscreenDetectorAdapter(), FullscreenDetector)


def test_autostart_manager_adapter_satisfies_protocol() -> None:
    assert isinstance(AutostartManagerAdapter(), AutostartManager)


def test_config_repository_adapter_satisfies_protocol() -> None:
    assert isinstance(ConfigRepositoryAdapter(), ConfigRepository)


def test_state_repository_adapter_satisfies_protocol() -> None:
    assert isinstance(StateRepositoryAdapter(), StateRepository)


# ── Delegation checks (smoke — real modules are exercised) ───────


def test_idle_adapter_returns_float() -> None:
    result = IdleDetectorAdapter().get_idle_seconds()
    assert isinstance(result, float)
    assert result >= 0.0


def test_fullscreen_adapter_returns_bool() -> None:
    result = FullscreenDetectorAdapter().is_foreground_fullscreen()
    assert isinstance(result, bool)


def test_autostart_adapter_round_trip() -> None:
    manager = AutostartManagerAdapter()
    # Save current state, toggle, then restore
    original = manager.is_enabled()
    assert isinstance(original, bool)

    manager.set_enabled(not original)
    assert manager.is_enabled() is not original

    manager.set_enabled(original)
    assert manager.is_enabled() is original


def test_config_repository_load_returns_app_config() -> None:
    from app.config import AppConfig

    repo = ConfigRepositoryAdapter()
    config = repo.load()
    assert isinstance(config, AppConfig)
    assert config.reminder_interval_minutes > 0


def test_config_repository_save_round_trip(tmp_path) -> None:
    from app.config import AppConfig, CONFIG_PATH

    repo = ConfigRepositoryAdapter()
    # Save a modified config
    modified = AppConfig(reminder_interval_minutes=10)
    repo.save(modified)

    # Verify by loading directly from disk
    # (repo.load might return cached — force a fresh read)
    from app.config import load_config as raw_load

    loaded = raw_load(CONFIG_PATH)
    assert loaded.reminder_interval_minutes == 10


def test_state_repository_load_returns_app_state() -> None:
    from app.state import AppState

    repo = StateRepositoryAdapter()
    state = repo.load()
    assert isinstance(state, AppState)