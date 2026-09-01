import json
from pathlib import Path

from app.core.event_bus import EventBus
from app.core.events import (
    Paused,
    ReminderCompleted,
    ReminderDismissed,
    ReminderTriggered,
    TodayPauseStarted,
)
from app.stats import StatsTracker, UsageStats, completion_rate


def test_manual_break_does_not_increase_scheduled_reminder_count(
    tmp_path: Path,
) -> None:
    bus = EventBus()
    tracker = StatsTracker(bus, tmp_path / "stats.json")

    bus.publish(
        ReminderTriggered(
            source="manual", duration_seconds=20, pause_minutes=60
        )
    )

    assert tracker.stats == UsageStats()


def test_events_update_their_matching_counters(tmp_path: Path) -> None:
    bus = EventBus()
    tracker = StatsTracker(bus, tmp_path / "stats.json")

    bus.publish(ReminderTriggered(source="scheduled", duration_seconds=20, pause_minutes=60))
    bus.publish(ReminderCompleted(source="scheduled"))
    bus.publish(ReminderDismissed(source="scheduled"))
    bus.publish(Paused(paused_until=100, pause_minutes=5))
    bus.publish(TodayPauseStarted())

    assert tracker.stats == UsageStats(
        reminder_count=1,
        completed_count=1,
        skip_count=1,
        pause_count=2,
    )


def test_manual_outcomes_do_not_change_planned_counters(tmp_path: Path) -> None:
    bus = EventBus()
    tracker = StatsTracker(bus, tmp_path / "stats.json")

    bus.publish(ReminderCompleted(source="manual"))
    bus.publish(ReminderDismissed(source="manual"))

    assert tracker.stats == UsageStats()


def test_stats_persist_and_malformed_file_recovers_to_zero(tmp_path: Path) -> None:
    path = tmp_path / "stats.json"
    bus = EventBus()
    tracker = StatsTracker(bus, path)
    bus.publish(ReminderTriggered(source="scheduled", duration_seconds=20, pause_minutes=60))

    restored = StatsTracker(EventBus(), path)
    assert restored.stats.reminder_count == 1

    path.write_text("{broken", encoding="utf-8")
    assert StatsTracker(EventBus(), path).stats == UsageStats()


def test_invalid_counter_values_are_loaded_as_zero(tmp_path: Path) -> None:
    path = tmp_path / "stats.json"
    path.write_text(
        json.dumps(
            {
                "reminder_count": -1,
                "completed_count": True,
                "skip_count": 1.5,
                "pause_count": 2,
            }
        ),
        encoding="utf-8",
    )

    assert StatsTracker(EventBus(), path).stats == UsageStats(pause_count=2)


def test_completion_rate_handles_zero_denominator() -> None:
    assert completion_rate(UsageStats()) is None
    assert completion_rate(UsageStats(reminder_count=4, completed_count=3)) == 0.75
