"""The game loop.

It runs rounds, reports outcomes through the event port, and asks the
difficulty port for the next difficulty. It names no adapter: a template that
wires an unconfigured port must fail loudly here, not silently degrade.

Every tunable -- starting difficulty, speed, board size, obstacle count --
is read from the injected knob store on each match start and each round,
never from a literal. The loop keeps an explicit match lifecycle: a round
cannot run before a match starts, a paused match refuses progress until
it is resumed, and ``end_match()`` marks the boundary the between-games
tuning reads across. ``restart()`` turns that boundary into one atomic
transition: the finished match ends and a fresh one begins, reading the
knob store anew so between-games retuning lands without any limbo state.
"""

from dataclasses import dataclass
from typing import Any, Mapping

from game_core.difficulty import AdaptiveDifficulty, DifficultyObservation
from game_core.events import DomainEvent, EventPublisher
from game_core.match_parameters import MatchKnobs

MATCH_STARTED_EVENT = "match.started"
MATCH_PAUSED_EVENT = "match.paused"
MATCH_RESUMED_EVENT = "match.resumed"
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
        self._match_paused = False

    @property
    def difficulty(self) -> float:
        """The difficulty in force for the next round."""
        return self._difficulty

    @property
    def paused(self) -> bool:
        """Whether the live match is currently frozen by a pause."""
        return self._match_paused

    def start_match(self) -> None:
        """Begin a match by reading every tunable from the knob store."""
        if self._match_in_progress:
            raise ValueError(
                "a match is already in progress; end it before starting another"
            )
        self._match_in_progress = True
        self._match_paused = False
        self._difficulty = self._knobs.starting_difficulty
        self._publish(MATCH_STARTED_EVENT, self._match_parameters_reported())

    def pause(self) -> None:
        """Freeze the live match: rounds refuse to run until it resumes."""
        self._require_a_live_unpaused_match(action="pause")
        self._match_paused = True
        self._publish(MATCH_PAUSED_EVENT, {})

    def resume(self) -> None:
        """Unfreeze a paused match, letting rounds run again."""
        self._require_a_paused_match()
        self._match_paused = False
        self._publish(MATCH_RESUMED_EVENT, {})

    def restart(self) -> None:
        """End the running match and begin a fresh one in one transition.

        The single call exists so a death needs no limbo state between the
        two matches, and because the fresh start reads the knob store
        anew it is the hook point where the AI retunes between games.
        """
        self._require_a_live_match(action="restart")
        self.end_match()
        self.start_match()

    def end_match(self) -> None:
        """Mark the match finished, freeing the loop to start a new one."""
        if not self._match_in_progress:
            raise ValueError("no match is in progress to end")
        self._match_in_progress = False

    def play_round(self, player_succeeded: bool) -> RoundResult:
        """Run one round: report it, then hand the outcome to the strategy."""
        if self._match_paused:
            raise ValueError(
                "the match is paused; resume it before playing a round"
            )
        if not self._match_in_progress:
            raise ValueError(
                "no match is running; call start_match() to begin one"
            )
        self._publish(ROUND_STARTED_EVENT, self._round_parameters_in_force())
        observation = DifficultyObservation(player_succeeded=player_succeeded)
        self._difficulty = self._difficulty_strategy.adjust(
            self._difficulty, observation
        )
        self._publish(DIFFICULTY_ADJUSTED_EVENT, {"difficulty": self._difficulty})
        return RoundResult(
            difficulty=self._difficulty, player_succeeded=player_succeeded
        )

    def _require_a_live_unpaused_match(self, action: str) -> None:
        """Refuse an action that needs a live, unpaused match."""
        self._require_a_live_match(action=action)
        if self._match_paused:
            raise ValueError(
                f"the match is paused; only resume() may leave the pause, "
                f"not {action}()"
            )

    def _require_a_live_match(self, action: str) -> None:
        """Refuse an action that cannot run without a live match."""
        if not self._match_in_progress:
            raise ValueError(f"no match is running to {action}")

    def _require_a_paused_match(self) -> None:
        """Refuse a resume with no paused match behind it."""
        if not self._match_in_progress or not self._match_paused:
            raise ValueError(
                "no match is paused to resume;"
                " resume() follows a pause() on a live match"
            )

    def _physical_parameters_from_the_store(self) -> dict[str, Any]:
        """The three physical tunables exactly as the store holds them."""
        return {
            "speed": self._knobs.speed,
            "board_size": self._knobs.board_size,
            "obstacle_count": self._knobs.obstacle_count,
        }

    def _match_parameters_reported(self) -> dict[str, Any]:
        parameters: dict[str, Any] = {
            "starting_difficulty": self._knobs.starting_difficulty
        }
        parameters.update(self._physical_parameters_from_the_store())
        return parameters

    def _round_parameters_in_force(self) -> dict[str, Any]:
        parameters: dict[str, Any] = {"difficulty": self._difficulty}
        parameters.update(self._physical_parameters_from_the_store())
        return parameters

    def _publish(self, event_name: str, payload: Mapping[str, Any]) -> None:
        self._event_publisher.publish(
            DomainEvent(name=event_name, payload=payload)
        )
