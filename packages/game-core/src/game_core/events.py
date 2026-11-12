"""The event port the loop publishes through.

game-core defines only the contract: what happened and a small payload. Any
real destination (an in-memory sink, a log, telemetry) is an adapter that
implements the port and lives outside this module.
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
