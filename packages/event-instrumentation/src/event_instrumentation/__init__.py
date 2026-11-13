"""event-instrumentation: implementations of the event contract it pins.

The module imports nothing from the engine, so copied templates keep this
swap point without tangled dependencies.
"""

from event_instrumentation.contracts.event_publisher.v1 import (
    DomainEvent,
    EventPublisher,
)
from event_instrumentation.in_memory_sink import (
    InMemoryEventSink,
    RecordedEvent,
)

__all__ = [
    "DomainEvent",
    "EventPublisher",
    "InMemoryEventSink",
    "RecordedEvent",
]
