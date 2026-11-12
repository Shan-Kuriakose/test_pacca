"""event-instrumentation: adapters for game-core's EventPublisher port.

This module imports nothing from game-core. It satisfies the
EventPublisher port structurally, recording what the loop emits without the
instrumentation layer knowing anything about the loop's internals.
"""

from event_instrumentation.in_memory_sink import InMemoryEventSink

__all__ = ["InMemoryEventSink"]
