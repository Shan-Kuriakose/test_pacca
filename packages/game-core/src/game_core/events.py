"""The event port the loop publishes through.

game-core defines only the contract: what happened and a small payload. Any
real destination (an in-memory sink, a log, telemetry) is an adapter that
implements the port and lives outside this module. The contract itself stays
in a versioned file that adapters can pin exactly.
"""

from game_core.contracts.event_publisher.v1 import (
    DomainEvent,
    EventPublisher,
)

__all__ = ["DomainEvent", "EventPublisher"]
