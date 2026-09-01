from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from app.core.event_bus import EventBus
from app.core.events import (
    Paused,
    ReminderCompleted,
    ReminderDismissed,
    ReminderTriggered,
    TodayPauseStarted,
)
from app.paths import STATS_PATH
from app.persistence import atomic_write_json, read_json_object


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UsageStats:
    reminder_count: int = 0
    completed_count: int = 0
    skip_count: int = 0
    pause_count: int = 0


def completion_rate(stats: UsageStats) -> float | None:
    if stats.reminder_count == 0:
        return None
    return stats.completed_count / stats.reminder_count


def format_completion_rate(stats: UsageStats) -> str:
    rate = completion_rate(stats)
    return "暂无数据" if rate is None else f"{rate:.0%}"


class StatsTracker:
    def __init__(self, bus: EventBus, path: Path = STATS_PATH) -> None:
        self._path = Path(path)
        self._stats = self._load()
        self._unsubs = [
            bus.subscribe(ReminderTriggered, self._on_reminder_triggered),
            bus.subscribe(ReminderCompleted, self._on_reminder_completed),
            bus.subscribe(ReminderDismissed, self._on_reminder_dismissed),
            bus.subscribe(Paused, self._on_paused),
            bus.subscribe(TodayPauseStarted, self._on_today_pause_started),
        ]

    @property
    def stats(self) -> UsageStats:
        return self._stats

    def reset(self) -> None:
        self._stats = UsageStats()
        self._save()

    def _load(self) -> UsageStats:
        raw = read_json_object(self._path, {}, backup=True)
        return UsageStats(
            reminder_count=_non_negative_int(raw.get("reminder_count")),
            completed_count=_non_negative_int(raw.get("completed_count")),
            skip_count=_non_negative_int(raw.get("skip_count")),
            pause_count=_non_negative_int(raw.get("pause_count")),
        )

    def _on_reminder_triggered(self, event: ReminderTriggered) -> None:
        if event.source == "scheduled":
            self._increment("reminder_count")

    def _on_reminder_completed(self, event: ReminderCompleted) -> None:
        if event.source == "scheduled":
            self._increment("completed_count")

    def _on_reminder_dismissed(self, event: ReminderDismissed) -> None:
        if event.source == "scheduled":
            self._increment("skip_count")

    def _on_paused(self, event: Paused) -> None:
        self._increment("pause_count")

    def _on_today_pause_started(self, event: TodayPauseStarted) -> None:
        self._increment("pause_count")

    def _increment(self, field: str) -> None:
        self._stats = replace(
            self._stats,
            **{field: getattr(self._stats, field) + 1},
        )
        self._save()

    def _save(self) -> None:
        try:
            atomic_write_json(self._path, asdict(self._stats))
        except OSError:
            logger.exception("Could not save usage statistics to %s", self._path)


def _non_negative_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value
