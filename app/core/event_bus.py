"""Type-safe publish/subscribe event bus.

Design:
- Subscribers register by event type (class).
- Publish dispatches to all subscribers of that exact type.
- Subscriber exceptions are caught and logged — one bad subscriber
  never starves the rest.
- Thread-safe via a reentrant lock (tray icon callbacks arrive on
  a background thread; core logic runs on the Tk main loop).
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from typing import TypeVar

from app.core.events import (
    ConfigChanged,
    ExitRequested,
    FloatingCountdownToggled,
    FullscreenDetected,
    FullscreenEnded,
    IdleDetected,
    IdleEnded,
    Paused,
    ReminderDismissed,
    ReminderTriggered,
    Resumed,
    StateChanged,
    Tick,
    TimerStarted,
    TimerStopped,
)

logger = logging.getLogger(__name__)

# All event types — used for type checking at registration time.
Event = (
    TimerStarted
    | TimerStopped
    | Tick
    | ReminderTriggered
    | ReminderDismissed
    | StateChanged
    | IdleDetected
    | IdleEnded
    | FullscreenDetected
    | FullscreenEnded
    | Paused
    | Resumed
    | ConfigChanged
    | FloatingCountdownToggled
    | ExitRequested
)

E = TypeVar("E")

Subscriber = Callable[[object], None]


class EventBus:
    """Central pub/sub hub connecting core domain to UI and platform layers."""

    def __init__(self) -> None:
        self._subscribers: dict[type, list[Subscriber]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> Callable[[], None]:
        """Register *handler* for events of *event_type*.

        Returns an unsubscribe callable — call it to remove the handler.
        """
        with self._lock:
            self._subscribers[event_type].append(handler)  # type: ignore[arg-type]

        def _unsubscribe() -> None:
            with self._lock:
                handlers = self._subscribers.get(event_type, [])
                if handler in handlers:
                    handlers.remove(handler)  # type: ignore[arg-type]

        return _unsubscribe

    def publish(self, event: object) -> None:
        """Dispatch *event* to all subscribers registered for its type.

        Subscriber exceptions are caught and logged so that a single
        failing subscriber cannot block the rest of the dispatch.
        """
        with self._lock:
            # Copy the list under lock to avoid mutation-during-iteration.
            handlers = list(self._subscribers.get(type(event), []))

        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "EventBus subscriber %r failed for event %r",
                    handler,
                    type(event).__name__,
                )

    def clear(self) -> None:
        """Remove all subscribers. Mainly useful in tests."""
        with self._lock:
            self._subscribers.clear()

    def subscriber_count(self, event_type: type) -> int:
        """Return the number of subscribers for *event_type* (mainly for tests)."""
        with self._lock:
            return len(self._subscribers.get(event_type, []))
