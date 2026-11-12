"""The in-memory event sink: the adapter a copied template starts with.

Swap this for a persistent or remote sink when a project outgrows it; the
loop only needs something that answers ``publish(event)``.
"""


class InMemoryEventSink:
    """Record every published event in memory for inspection."""

    def __init__(self) -> None:
        self._events = []

    def publish(self, event) -> None:
        if event is None:
            raise ValueError("InMemoryEventSink requires an event; got None.")
        self._events.append(event)

    def events(self) -> tuple:
        """Every event published so far, oldest first."""
        return tuple(self._events)

    def events_of_type(self, event_type: str) -> tuple:
        """Every published event of one type, oldest first."""
        return tuple(
            event for event in self._events if event.event_type == event_type
        )

    def clear(self) -> None:
        """Forget every recorded event."""
        self._events.clear()
