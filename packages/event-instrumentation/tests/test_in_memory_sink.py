"""Behaviour of the in-memory sink, including its refusal path."""

import pytest

from event_instrumentation import InMemoryEventSink


class FakeEvent:
    """Stands in for the event dataclass game-core emits through the port."""

    def __init__(self, topic: str) -> None:
        self.topic = topic


def test_the_sink_records_every_published_event():
    event_sink = InMemoryEventSink()
    first_event = FakeEvent("round.completed")
    second_event = FakeEvent("difficulty.adjusted")

    event_sink.publish(first_event)
    event_sink.publish(second_event)

    assert event_sink.events() == (first_event, second_event)


def test_a_fresh_sink_reads_empty():
    assert InMemoryEventSink().events() == ()


def test_the_sink_filters_by_topic():
    event_sink = InMemoryEventSink()
    completion = FakeEvent("round.completed")
    event_sink.publish(completion)
    event_sink.publish(FakeEvent("difficulty.adjusted"))

    assert event_sink.events(topic="round.completed") == (completion,)


def test_a_filtered_read_of_another_topic_is_empty():
    event_sink = InMemoryEventSink()
    event_sink.publish(FakeEvent("round.completed"))

    assert event_sink.events(topic="difficulty.adjusted") == ()


def test_publishing_a_missing_event_is_refused_not_recorded():
    event_sink = InMemoryEventSink()

    with pytest.raises(ValueError):
        event_sink.publish(None)

    assert event_sink.events() == ()


def test_clearing_removes_every_recorded_event():
    event_sink = InMemoryEventSink()
    event_sink.publish(FakeEvent("round.completed"))

    event_sink.clear()

    assert event_sink.events() == ()
