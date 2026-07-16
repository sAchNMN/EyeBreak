"""Concrete adapter classes for the platform Protocol interfaces.

Each adapter wraps the existing module-level functions from
``app.idle``, ``app.fullscreen``, ``app.autostart``, ``app.config``,
and ``app.state`` into a class that satisfies the corresponding
``runtime_checkable`` Protocol.

Usage
-----
Instead of importing ``get_idle_seconds`` directly, create an
``IdleDetectorAdapter`` and pass it to ``TimerEngine``:

    engine = TimerEngine(
        ...,
        idle_detector=IdleDetectorAdapter(),
        fullscreen_detector=FullscreenDetectorAdapter(),
        autostart_manager=AutostartManagerAdapter(),
        ...
    )

In tests, swap in one of the ``Fake*`` classes from
``tests/test_timer_engine.py`` instead.
"""

from __future__ import annotations

from app.autostart import is_autostart_enabled, set_autostart
from app.config import AppConfig, load_config, save_config
from app.fullscreen import is_foreground_window_fullscreen
from app.idle import get_idle_seconds
from app.state import AppState, load_app_state, save_app_state


# ── IdleDetector ─────────────────────────────────────────────────


class IdleDetectorAdapter:
    """Satisfies ``IdleDetector`` by delegating to ``app.idle.get_idle_seconds``."""

    __slots__ = ()

    def get_idle_seconds(self) -> float:
        return get_idle_seconds()


# ── FullscreenDetector ───────────────────────────────────────────


class FullscreenDetectorAdapter:
    """Satisfies ``FullscreenDetector`` by delegating to ``app.fullscreen``."""

    __slots__ = ()

    def is_foreground_fullscreen(self) -> bool:
        return is_foreground_window_fullscreen()


# ── AutostartManager ─────────────────────────────────────────────


class AutostartManagerAdapter:
    """Satisfies ``AutostartManager`` by delegating to ``app.autostart``."""

    __slots__ = ()

    def is_enabled(self) -> bool:
        return is_autostart_enabled()

    def set_enabled(self, enabled: bool) -> None:
        set_autostart(enabled)


# ── ConfigRepository ─────────────────────────────────────────────


class ConfigRepositoryAdapter:
    """Satisfies ``ConfigRepository`` by delegating to ``app.config``.

    The ``load`` / ``save`` methods return and accept ``AppConfig``
    instances respectively.
    """

    __slots__ = ()

    def load(self) -> AppConfig:
        return load_config()

    def save(self, config: AppConfig) -> None:
        save_config(config)


# ── StateRepository ──────────────────────────────────────────────


class StateRepositoryAdapter:
    """Satisfies ``StateRepository`` by delegating to ``app.state``.

    The ``load`` / ``save`` methods return and accept ``AppState``
    instances respectively.
    """

    __slots__ = ()

    def load(self) -> AppState:
        return load_app_state()

    def save(self, state: AppState) -> None:
        save_app_state(state)