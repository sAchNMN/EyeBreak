"""Protocol interfaces for platform-specific operations.

The core domain layer depends on these protocols, never on concrete
implementations. This allows unit-testing the core without Windows APIs
(inject a fake) and documents exactly what the core needs.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class IdleDetector(Protocol):
    """Detects user idle time (seconds since last keyboard/mouse input)."""

    def get_idle_seconds(self) -> float:
        """Return seconds since last user input. 0.0 if unknown/unavailable."""
        ...


@runtime_checkable
class FullscreenDetector(Protocol):
    """Detects whether the foreground window is fullscreen."""

    def is_foreground_fullscreen(self) -> bool:
        """Return True if the foreground window covers the monitor."""
        ...


@runtime_checkable
class AutostartManager(Protocol):
    """Manages OS-level autostart registration."""

    def is_enabled(self) -> bool:
        """Return True if autostart is currently registered."""
        ...

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable autostart registration."""
        ...
