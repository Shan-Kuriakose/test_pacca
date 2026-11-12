"""game-core: the template's game loop and its ports, and nothing else.

Adapters live in sibling modules (difficulty-ai, event-instrumentation) and
are supplied to the loop through the ports re-exported here.
"""

from game_core.difficulty import AdaptiveDifficulty
from game_core.events import DomainEvent, EventPublisher
from game_core.loop import GameLoop

__all__ = ["AdaptiveDifficulty", "DomainEvent", "EventPublisher", "GameLoop"]
