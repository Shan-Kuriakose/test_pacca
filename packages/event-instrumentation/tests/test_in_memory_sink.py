"""InMemoryEventSink: recording, filtering, empty reads and refusals."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from event_instrumentation.in_memory_sink import InMemoryEventSink  # noqa: E402


class AnEvent:
    """A stand-in for a real domain event; the sink depends on no concrete type."""

    def __init__(self, event_type: str) -> None:
        self.event_type = event_type


def test_a_fresh_sink_reads_as_empty():
    sink = InMemoryEventSink()

    assert sink.events() == ()
    assert sink.events_of_type("anything") == ()


def test_publish_records_events_oldest_first():
    sink = InMemoryEventSink()
    first, second = AnEvent("a"), AnEvent("b")

    sink.publish(first)
    sink.publish(second)

    assert sink.events() == (first, second)


def test_events_of_type_returns_only_that_type():
    sink = InMemoryEventSink()
    kept, filtered = AnEvent("round_played"), AnEvent("difficulty_changed")
    sink.publish(kept)
    sink.publish(filtered)

    assert sink.events_of_type("round_played") == (kept,)


def test_clear_forgives_nothing_and_removes_every_event():
    sink = InMemoryEventSink()
    sink.publish(AnEvent("round_played"))

    sink.clear()

    assert sink.events() == ()


def test_publishing_a_missing_event_fails_loudly():
    sink = InMemoryEventSink()

    with pytest.raises(ValueError, match="event"):
        sink.publish(None)
