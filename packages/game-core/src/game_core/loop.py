"""The game loop.

It runs rounds inside an explicit match lifecycle, reports outcomes through
the event port, and asks the difficulty port for the next difficulty. It
names no adapter: a template that wires an unconfigured port must fail loudly
here, not silently degrade.

Every tunable -- starting difficulty, speed, board size, obstacle count --
is read from the injected knob store on each match start and each round,
never from a literal.
"""

from dataclasses import dataclass
from typing import Any, Mapping

from game_core.difficulty import AdaptiveDifficulty, DifficultyObservation
from game_core.events import DomainEvent, EventPublisher
from game_core.match_parameters import MatchKnobs

MATCH_STARTED_EVENT = "match.started"
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
        knobs: MatchKnobs | None = None,
    ) -> None:
        self._event_publisher = _required_port(event_publisher, "event publisher")
        self._difficulty_strategy = _required_port(
            difficulty_strategy, "difficulty strategy"
        )
        self._knobs = knobs if knobs is not None else MatchKnobs()
        self._difficulty = self._knobs.starting_difficulty
        self._match_in_progress = False
        self._rounds_played_in_match = 0

    @property
    def difficulty(self) -> float:
        """The difficulty in force for the next round."""
        return self._difficulty

    def start_match(self) -> None:
        """Begin a match by reading every tunable from the knob store.

        Once a match has played a round, starting another is refused loudly:
        call finish_match() to close it first, so between-games tuning is
        never mistaken for a mid-match reset. Before its first round a match
        has played nothing, so start_match() simply re-reads the freshly
        tuned store.
        """
        if self._match_in_progress and self._rounds_played_in_match > 0:
            raise ValueError(
                "a match is already in progress; call finish_match() "
                "before starting another"
            )
        self._difficulty = self._knobs.starting_difficulty
        self._match_in_progress = True
        self._rounds_played_in_match = 0
        self._publish(
            MATCH_STARTED_EVENT,
            {
                "starting_difficulty": self._knobs.starting_difficulty,
                "speed": self._knobs.speed,
                "board_size": self._knobs.board_size,
                "obstacle_count": self._knobs.obstacle_count,
            },
        )

    def finish_match(self) -> None:
        """Close the current match so a fresh one may start between games."""
        if not self._match_in_progress:
            raise ValueError("no match is in progress; nothing to finish")
        self._match_in_progress = False

    def play_round(self, player_succeeded: bool) -> RoundResult:
        """Run one round: report it, then hand the outcome to the strategy.

        Refuses loudly before a match has started: a round played outside
        the lifecycle must never resemble a round played inside it.
        """
        if not self._match_in_progress:
            raise ValueError(
                "no match is in progress; call start_match() before playing a round"
            )
        self._rounds_played_in_match += 1
        self._publish(ROUND_STARTED_EVENT, self._parameters_in_force())
        observation = DifficultyObservation(player_succeeded=player_succeeded)
        self._difficulty = self._difficulty_strategy.adjust(
            self._difficulty, observation
        )
        self._publish(DIFFICULTY_ADJUSTED_EVENT, {"difficulty": self._difficulty})
        return RoundResult(
            difficulty=self._difficulty, player_succeeded=player_succeeded
        )

    def _parameters_in_force(self) -> dict[str, Any]:
        parameters: dict[str, Any] = {"difficulty": self._difficulty}
        parameters.update(
            speed=self._knobs.speed,
            board_size=self._knobs.board_size,
            obstacle_count=self._knobs.obstacle_count,
        )
        return parameters

    def _publish(self, event_name: str, payload: Mapping[str, Any]) -> None:
        self._event_publisher.publish(
            DomainEvent(name=event_name, payload=payload)
        )
