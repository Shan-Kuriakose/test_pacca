"""Version 1 of the event contract consumed by event-instrumentation.

Each adapter pins a byte-for-byte copy of this contract rather than importing
game-core, so the modules remain independently deployable.
"""

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class DomainEvent:
    """Something that happened in the game that the loop wants observed."""

    name: str
    payload: Mapping[str, Any] = field(default_factory=dict)


class EventPublisher(Protocol):
    """Port every event destination must satisfy; adapters implement it."""

    def publish(self, event: DomainEvent) -> None: ...


__all__ = ["DomainEvent", "EventPublisher"]
