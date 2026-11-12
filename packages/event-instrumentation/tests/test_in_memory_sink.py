"""Sink behaviour: recording, ordering, filtering, eviction, and refusals."""

import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import pytest

import event_instrumentation
from event_instrumentation import InMemoryEventSink, RecordedEvent


class IncomingEvent:
    """A stand-in event, shaped like the ones the loop publishes."""

    def __init__(self, name: str, payload: dict | None = None) -> None:
        self.name = name
        self.payload = dict(payload or {})


def make_sink(capacity: int = 1_000) -> InMemoryEventSink:
    return InMemoryEventSink(capacity=capacity)


def test_an_empty_sink_records_nothing():
    sink = make_sink()

    assert sink.events() == ()


def test_a_published_event_is_recorded_with_its_name_and_payload():
    sink = make_sink()

    sink.publish(IncomingEvent("round.started", {"difficulty": 0.5}))

    recorded = sink.events()
    assert recorded == (
        RecordedEvent(name="round.started", payload={"difficulty": 0.5}),
    )


def test_events_are_recorded_in_publish_order():
    sink = make_sink()

    sink.publish(IncomingEvent("round.started"))
    sink.publish(IncomingEvent("difficulty.adjusted"))
    sink.publish(IncomingEvent("round.started"))

    assert [event.name for event in sink.events()] == [
        "round.started",
        "difficulty.adjusted",
        "round.started",
    ]


def test_events_named_keeps_only_the_matching_name():
    sink = make_sink()

    sink.publish(IncomingEvent("round.started"))
    sink.publish(IncomingEvent("difficulty.adjusted"))

    matched = sink.events_named("difficulty.adjusted")
    assert [event.name for event in matched] == ["difficulty.adjusted"]


def test_events_named_of_an_unknown_name_is_empty():
    sink = make_sink()

    sink.publish(IncomingEvent("round.started"))

    assert sink.events_named("round.finished") == ()


def test_a_full_sink_evicts_its_oldest_record_first():
    sink = make_sink(capacity=2)

    sink.publish(IncomingEvent("first"))
    sink.publish(IncomingEvent("second"))
    sink.publish(IncomingEvent("third"))

    assert [event.name for event in sink.events()] == ["second", "third"]


def test_clearing_the_sink_forgets_every_record():
    sink = make_sink()

    sink.publish(IncomingEvent("round.started"))
    sink.clear()

    assert sink.events() == ()


def test_a_sink_that_cannot_keep_anything_is_refused_loudly():
    with pytest.raises(ValueError, match="at least one event"):
        make_sink(capacity=0)


def test_a_recorded_event_is_immune_to_later_payload_edits():
    sink = make_sink()
    payload = {"difficulty": 0.5}

    sink.publish(IncomingEvent("round.started", payload))
    payload["difficulty"] = 0.9

    (recorded,) = sink.events()
    assert recorded.payload == {"difficulty": 0.5}


def test_the_module_publishes_its_public_surface():
    assert "InMemoryEventSink" in event_instrumentation.__all__
    assert "RecordedEvent" in event_instrumentation.__all__
