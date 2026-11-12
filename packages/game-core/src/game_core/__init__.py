"""game-core: the game loop and the ports it calls out to.

The loop is the highest-level policy of the template. It depends only on the
ports defined beside it; every concrete capability (an adaptive strategy, an
event sink) is supplied from outside as an adapter.
"""

from game_core.difficulty import DifficultyObservation, AdaptiveDifficulty
from game_core.events import DomainEvent, EventPublisher
from game_core.loop import GameLoop, RoundResult

__all__ = [
    "AdaptiveDifficulty",
    "DifficultyObservation",
    "DomainEvent",
    "EventPublisher",
    "GameLoop",
    "RoundResult",
]
