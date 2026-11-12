"""The round loop: the template's highest-level policy.

It depends only on the ports in this package. How events are stored and how
difficulty is decided are details supplied from the outside.
"""

from dataclasses import dataclass

from game_core.difficulty import AdaptiveDifficulty, PlayerOutcome
from game_core.events import (
    DIFFICULTY_ADJUSTED_TOPIC,
    ROUND_COMPLETED_TOPIC,
    DomainEvent,
    EventPublisher,
)

DIFFICULTY_FLOOR = 1


class MissingIntegrationError(RuntimeError):
    """Raised when the loop is built without an integration it cannot default."""


@dataclass(frozen=True)
class RoundReport:
    """What one round consumed and produced."""

    round_number: int
    difficulty: int
    outcome: PlayerOutcome


class GameLoop:
    """Runs rounds, publishing events and consulting the difficulty port."""

    def __init__(
        self,
        event_publisher: EventPublisher,
        difficulty_strategy: AdaptiveDifficulty,
        starting_difficulty: int = DIFFICULTY_FLOOR,
    ) -> None:
        self._publisher = _require(event_publisher, "event publisher")
        self._difficulty_strategy = _require(
            difficulty_strategy, "difficulty strategy"
        )
        self._difficulty = starting_difficulty
        self._round_number = 0

    @property
    def difficulty(self) -> int:
        """The difficulty the next round will play at."""
        return self._difficulty

    def run_round(self, outcome: PlayerOutcome) -> RoundReport:
        """Play one round out of the outcome given, then adapt."""
        self._round_number += 1
        self._publish_round_completed(outcome)
        self._adjust_difficulty(outcome)
        return RoundReport(self._round_number, self._difficulty, outcome)

    def _publish_round_completed(self, outcome: PlayerOutcome) -> None:
        self._publisher.publish(
            DomainEvent(
                topic=ROUND_COMPLETED_TOPIC,
                payload={
                    "round": self._round_number,
                    "difficulty": self._difficulty,
                    "succeeded": outcome.succeeded,
                },
            )
        )

    def _adjust_difficulty(self, outcome: PlayerOutcome) -> None:
        proposed = self._difficulty_strategy.next_difficulty(
            self._difficulty, outcome
        )
        if proposed == self._difficulty:
            return
        self._publish_difficulty_adjusted(proposed)
        self._difficulty = proposed

    def _publish_difficulty_adjusted(self, proposed: int) -> None:
        self._publisher.publish(
            DomainEvent(
                topic=DIFFICULTY_ADJUSTED_TOPIC,
                payload={
                    "round": self._round_number,
                    "from": self._difficulty,
                    "to": proposed,
                },
            )
        )
        self._difficulty = proposed


def _require(integration: object, description: str) -> object:
    if integration is None:
        raise MissingIntegrationError(
            f"a {description} must be supplied; none is configured"
        )
    return integration
