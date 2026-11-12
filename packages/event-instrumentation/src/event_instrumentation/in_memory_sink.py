"""An event publisher adapter the copied template starts with.

It implements the publishing port by shape, importing nothing from
game-core, so the modules stay independently scoped.
"""

from typing import Iterator, Optional, Protocol


class PublishedEventShape(Protocol):
    """The event shape the port hands in; game-core's dataclass satisfies it."""

    @property
    def topic(self) -> str:
        ...


class InMemoryEventSink:
    """Records every published event; a silent drop never resembles a success."""

    def __init__(self) -> None:
        self._recorded_events: list = []

    def publish(self, event: PublishedEventShape) -> None:
        if event is None:
            raise ValueError(
            "an event must be supplied; a silent drop must never look published"
        )
        self._recorded_events.append(event)

    def events(self, topic: Optional[str] = None) -> tuple:
        return tuple(self._selected(topic))

    def clear(self) -> None:
        self._recorded_events = []

    def _selected(self, topic: Optional[str]) -> Iterator:
        for event in self._recorded_events:
            if topic is None or event.topic == topic:
                yield event
