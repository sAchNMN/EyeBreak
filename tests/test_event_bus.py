"""Tests for app.core.event_bus.EventBus."""

from dataclasses import dataclass

from app.core.event_bus import EventBus


# ── Test event types ────────────────────────────────────────────


@dataclass(frozen=True)
class _DummyEvent:
    value: int


@dataclass(frozen=True)
class _OtherEvent:
    text: str


# ── Subscribe + publish ─────────────────────────────────────────


def test_subscriber_receives_published_event() -> None:
    bus = EventBus()
    received: list[_DummyEvent] = []
    bus.subscribe(_DummyEvent, received.append)

    event = _DummyEvent(value=42)
    bus.publish(event)

    assert received == [event]


def test_multiple_subscribers_all_receive_event() -> None:
    bus = EventBus()
    sink_a: list[_DummyEvent] = []
    sink_b: list[_DummyEvent] = []
    bus.subscribe(_DummyEvent, sink_a.append)
    bus.subscribe(_DummyEvent, sink_b.append)

    event = _DummyEvent(value=1)
    bus.publish(event)

    assert sink_a == [event]
    assert sink_b == [event]


def test_subscriber_only_receives_its_event_type() -> None:
    bus = EventBus()
    dummy_sink: list[_DummyEvent] = []
    other_sink: list[_OtherEvent] = []
    bus.subscribe(_DummyEvent, dummy_sink.append)
    bus.subscribe(_OtherEvent, other_sink.append)

    bus.publish(_DummyEvent(value=1))
    bus.publish(_OtherEvent(text="hello"))

    assert dummy_sink == [_DummyEvent(value=1)]
    assert other_sink == [_OtherEvent(text="hello")]


def test_publish_with_no_subscribers_is_safe() -> None:
    bus = EventBus()
    # Should not raise.
    bus.publish(_DummyEvent(value=0))


# ── Unsubscribe ─────────────────────────────────────────────────


def test_unsubscribe_removes_handler() -> None:
    bus = EventBus()
    received: list[_DummyEvent] = []
    unsubscribe = bus.subscribe(_DummyEvent, received.append)

    bus.publish(_DummyEvent(value=1))
    assert len(received) == 1

    unsubscribe()
    bus.publish(_DummyEvent(value=2))
    assert len(received) == 1  # Still just the first event.


def test_unsubscribe_is_idempotent() -> None:
    bus = EventBus()
    received: list[_DummyEvent] = []
    unsubscribe = bus.subscribe(_DummyEvent, received.append)

    unsubscribe()
    unsubscribe()  # Second call should not raise.
    bus.publish(_DummyEvent(value=1))
    assert received == []


def test_unsubscribe_only_removes_target_handler() -> None:
    bus = EventBus()
    sink_a: list[_DummyEvent] = []
    sink_b: list[_DummyEvent] = []
    unsub_a = bus.subscribe(_DummyEvent, sink_a.append)
    bus.subscribe(_DummyEvent, sink_b.append)

    unsub_a()
    bus.publish(_DummyEvent(value=1))

    assert sink_a == []
    assert sink_b == [_DummyEvent(value=1)]


# ── Error isolation ─────────────────────────────────────────────


def test_failing_subscriber_does_not_block_others() -> None:
    bus = EventBus()
    good_sink: list[_DummyEvent] = []

    def bad_handler(_event: _DummyEvent) -> None:
        raise RuntimeError("boom")

    bus.subscribe(_DummyEvent, bad_handler)
    bus.subscribe(_DummyEvent, good_sink.append)

    event = _DummyEvent(value=99)
    bus.publish(event)  # Should not raise.

    assert good_sink == [event]  # Good subscriber still received it.


# ── Misc ────────────────────────────────────────────────────────


def test_subscriber_count() -> None:
    bus = EventBus()
    assert bus.subscriber_count(_DummyEvent) == 0

    bus.subscribe(_DummyEvent, lambda _e: None)
    assert bus.subscriber_count(_DummyEvent) == 1

    bus.subscribe(_DummyEvent, lambda _e: None)
    assert bus.subscriber_count(_DummyEvent) == 2


def test_clear_removes_all_subscribers() -> None:
    bus = EventBus()
    bus.subscribe(_DummyEvent, lambda _e: None)
    bus.subscribe(_OtherEvent, lambda _e: None)

    bus.clear()

    assert bus.subscriber_count(_DummyEvent) == 0
    assert bus.subscriber_count(_OtherEvent) == 0


def test_real_domain_events_flow_through_bus() -> None:
    """Smoke test: actual domain event types should work identically."""
    from app.core.events import ReminderTriggered, StateChanged, Tick

    bus = EventBus()
    ticks: list[Tick] = []
    state_changes: list[StateChanged] = []

    bus.subscribe(Tick, ticks.append)
    bus.subscribe(StateChanged, state_changes.append)

    bus.publish(Tick(remaining_seconds=59.0, display_text="00:59", display_color="#f9fafb"))
    bus.publish(StateChanged(old_state="RUNNING", new_state="PAUSED"))
    bus.publish(ReminderTriggered(duration_seconds=20, pause_minutes=60))  # No subscriber.

    assert len(ticks) == 1
    assert ticks[0].display_text == "00:59"
    assert len(state_changes) == 1
    assert state_changes[0].new_state == "PAUSED"
