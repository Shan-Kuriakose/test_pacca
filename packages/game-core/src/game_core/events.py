"""Domain events and the EventPublisher port the game loop emits through."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class DomainEvent:
    """One thing that happened inside a round, with what was known about it."""

    event_type: str
    payload: Mapping[str, object]


class EventPublisher(ABC):
    """Port the loop emits through; the instrumentation module supplies it."""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Deliver one domain event to wherever it is recorded."""
