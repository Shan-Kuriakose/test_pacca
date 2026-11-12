"""game-core: the round loop and the ports it depends on."""

from game_core.difficulty import AdaptiveDifficulty, PlayerOutcome
from game_core.events import (
    DIFFICULTY_ADJUSTED_TOPIC,
    ROUND_COMPLETED_TOPIC,
    DomainEvent,
    EventPublisher,
)
from game_core.loop import (
    DIFFICULTY_FLOOR,
    GameLoop,
    MissingIntegrationError,
    RoundReport,
)

__all__ = [
    "DIFFICULTY_ADJUSTED_TOPIC",
    "DIFFICULTY_FLOOR",
    "ROUND_COMPLETED_TOPIC",
    "AdaptiveDifficulty",
    "DomainEvent",
    "EventPublisher",
    "GameLoop",
    "MissingIntegrationError",
    "PlayerOutcome",
    "RoundReport",
]
