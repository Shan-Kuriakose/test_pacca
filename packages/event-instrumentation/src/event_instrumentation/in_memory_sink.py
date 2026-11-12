"""The in-memory event sink: the adapter a copied template starts with.

It keeps the events it is handed for inspection within the process. A
production destination (a message bus, a warehouse) is another module
implementing the same shape.
"""

from dataclasses import dataclass
from typing import Any, Mapping

DEFAULT_CAPACITY = 1_000


@dataclass(frozen=True)
class RecordedEvent:
    """The sink's own record of one published event."""

    name: str
    payload: Mapping[str, Any]


class InMemoryEventSink:
    """Records published events in memory, evicting the oldest when full."""

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        if capacity <= 0:
            raise ValueError(
                "the sink must keep at least one event; a sink that keeps "
                "nothing is not instrumentation"
            )
        self._capacity = capacity
        self._recorded: list[RecordedEvent] = []

    def publish(self, event: Any) -> None:
        """Record one event, dropping the oldest record when at capacity."""
        if len(self._recorded) == self._capacity:
            self._evict_oldest()
        self._recorded.append(
            RecordedEvent(name=event.name, payload=dict(event.payload))
        )

    def events(self) -> tuple[RecordedEvent, ...]:
        """Every recorded event, in publish order."""
        return tuple(self._recorded)

    def events_named(self, event_name: str) -> tuple[RecordedEvent, ...]:
        """Every recorded event of one name, in publish order."""
        return tuple(event for event in self._recorded if event.name == event_name)

    def clear(self) -> None:
        """Forget every recorded event."""
        self._recorded.clear()

    def _evict_oldest(self) -> None:
        del self._recorded[0]
