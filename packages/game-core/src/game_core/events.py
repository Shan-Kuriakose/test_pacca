"""Domain events and the event publishing port.

The domain owns this contract. Adapters in other modules implement it without
importing anything from game-core.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

ROUND_COMPLETED_TOPIC = "round.completed"
DIFFICULTY_ADJUSTED_TOPIC = "difficulty.adjusted"


@dataclass(frozen=True)
class DomainEvent:
    """A fact that already happened in the game domain."""

    topic: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    occurred_at: float = field(default_factory=time.time)


class EventPublisher(Protocol):
    """Port the game loop emits through; instrumentation supplies the adapter."""

    def publish(self, event: DomainEvent) -> None:
        """Accept one domain event and never lose it silently."""
        ...
