"""event-instrumentation: implementations of the event publisher port.

The module imports nothing from the engine: it records the event facts it is
handed into its own shape, so a copied template can replace this adapter
without the engine noticing.
"""

from event_instrumentation.in_memory_sink import InMemoryEventSink, RecordedEvent

__all__ = ["InMemoryEventSink", "RecordedEvent"]
