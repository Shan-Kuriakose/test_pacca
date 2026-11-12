"""The game loop.

It runs rounds, reports outcomes through the event port, and asks the
difficulty port for the next difficulty. It names no adapter: a template that
wires an unconfigured port must fail loudly here, not silently degrade.
"""

from dataclasses import dataclass

from game_core.difficulty import AdaptiveDifficulty, DifficultyObservation
from game_core.events import DomainEvent, EventPublisher

DEFAULT_DIFFICULTY = 0.5
ROUND_STARTED_EVENT = "round.started"
DIFFICULTY_ADJUSTED_EVENT = "difficulty.adjusted"


def _required_port(port: object, port_name: str) -> object:
    """Refuse an unwired integration at construction, loudly."""
    if port is None:
        raise ValueError(
            f"the game loop needs a {port_name}; an unconfigured integration "
            "must raise, never resemble a working one"
        )
    return port


@dataclass(frozen=True)
class RoundResult:
    """What one round of play produced."""

    difficulty: float
    player_succeeded: bool


class GameLoop:
    """Drives rounds; depends on its ports only, never on their adapters."""

    def __init__(
        self,
        event_publisher: EventPublisher,
        difficulty_strategy: AdaptiveDifficulty,
    ) -> None:
        self._event_publisher = _required_port(event_publisher, "event publisher")
        self._difficulty_strategy = _required_port(
            difficulty_strategy, "difficulty strategy"
        )
        self._difficulty = DEFAULT_DIFFICULTY

    @property
    def difficulty(self) -> float:
        """The difficulty in force for the next round."""
        return self._difficulty

    def play_round(self, player_succeeded: bool) -> RoundResult:
        """Run one round: report it, then hand the outcome to the strategy."""
        self._publish(ROUND_STARTED_EVENT, {"difficulty": self._difficulty})
        observation = DifficultyObservation(player_succeeded=player_succeeded)
        self._difficulty = self._difficulty_strategy.adjust(
            self._difficulty, observation
        )
        self._publish(DIFFICULTY_ADJUSTED_EVENT, {"difficulty": self._difficulty})
        return RoundResult(
            difficulty=self._difficulty, player_succeeded=player_succeeded
        )

    def _publish(self, event_name: str, payload: dict[str, float]) -> None:
        self._event_publisher.publish(
            DomainEvent(name=event_name, payload=payload)
        )
