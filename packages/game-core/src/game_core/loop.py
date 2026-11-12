"""The game loop: the template's highest-level policy.

It depends only on the ports in this module, never on the adapters that
implement them. That dependency rule is enforced as a test, not by review.
"""

from collections.abc import Mapping

from game_core.difficulty import AdaptiveDifficulty
from game_core.events import DomainEvent, EventPublisher

DEFAULT_STARTING_LEVEL = 1
ROUND_PLAYED_EVENT = "round_played"
DIFFICULTY_CHANGED_EVENT = "difficulty_changed"


class GameLoop:
    """Run rounds, publish what happened, and let the adapter set difficulty."""

    def __init__(
        self,
        publisher: EventPublisher,
        difficulty: AdaptiveDifficulty,
        starting_level: int = DEFAULT_STARTING_LEVEL,
    ) -> None:
        if publisher is None:
            raise ValueError("GameLoop requires an EventPublisher; got None.")
        if difficulty is None:
            raise ValueError("GameLoop requires an AdaptiveDifficulty; got None.")
        self._publisher = publisher
        self._difficulty = difficulty
        self._level = starting_level

    @property
    def level(self) -> int:
        """The level the next round runs at."""
        return self._level

    def play_round(self, outcome: str) -> int:
        """Play one round of `outcome`; return the next round's level."""
        self._publish(
            ROUND_PLAYED_EVENT, {"outcome": outcome, "level": self._level}
        )
        self._level = self._difficulty.next_level(self._level, outcome)
        self._publish(DIFFICULTY_CHANGED_EVENT, {"level": self._level})
        return self._level

    def _publish(self, event_type: str, payload: Mapping[str, object]) -> None:
        self._publisher.publish(DomainEvent(event_type, payload))
