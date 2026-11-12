"""The game loop.

It runs rounds, reports outcomes through the event port, and asks the
difficulty port for the next difficulty. It names no adapter: a template that
wires an unconfigured port must fail loudly here, not silently degrade.

A match moves through states: live, paused, dead. A pause freezes everything
and resume returns exactly where it left off; losing a round ends the match
in death, and restart asks the strategy to retune between games before play
opens again.
"""

from dataclasses import dataclass
from enum import Enum

from game_core.difficulty import AdaptiveDifficulty, DifficultyObservation
from game_core.events import DomainEvent, EventPublisher

DEFAULT_DIFFICULTY = 0.5
ROUND_STARTED_EVENT = "round.started"
DIFFICULTY_ADJUSTED_EVENT = "difficulty.adjusted"
GAME_PAUSED_EVENT = "game.paused"
GAME_RESUMED_EVENT = "game.resumed"
MATCH_ENDED_EVENT = "match.ended"
MATCH_RESTARTED_EVENT = "match.restarted"


class MatchState(Enum):
    """Where a match sits in its lifecycle."""

    LIVE = "live"
    PAUSED = "paused"
    DEAD = "dead"


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
        self._match_state = MatchState.LIVE
        self._rounds_played = 0

    @property
    def difficulty(self) -> float:
        """The difficulty in force for the next round."""
        return self._difficulty

    @property
    def match_state(self) -> MatchState:
        """Where the match sits in its lifecycle."""
        return self._match_state

    @property
    def rounds_played(self) -> int:
        """How many rounds this match has seen since it began."""
        return self._rounds_played

    def play_round(self, player_succeeded: bool) -> RoundResult:
        """Run one round: report it, then hand the outcome to the strategy."""
        self._assert_can_play_a_round()
        result = self._settle_round(player_succeeded)
        if not player_succeeded:
            self._end_match_in_death()
        return result

    def pause(self) -> None:
        """Freeze the match where it stands; only a live match pauses."""
        self._assert_match_is_live("a paused match")
        self._match_state = MatchState.PAUSED
        self._publish(GAME_PAUSED_EVENT, {"difficulty": self._difficulty})

    def resume(self) -> None:
        """Open play again exactly where the pause froze it."""
        if self._match_state is not MatchState.PAUSED:
            raise ValueError(
                f"{self._match_state.value} matches cannot resume; only a "
                "paused match resumes, and every refusal is loud"
            )
        self._match_state = MatchState.LIVE
        self._publish(GAME_RESUMED_EVENT, {"difficulty": self._difficulty})

    def restart(self) -> None:
        """Open a new match immediately by asking the strategy to retune."""
        if self._match_state is not MatchState.DEAD:
            raise ValueError(
                f"{self._match_state.value} matches cannot restart; restart "
                "follows a death, turning it straight into the next attempt"
            )
        self._difficulty = self._difficulty_strategy.restarted_match(
            self._difficulty
        )
        self._match_state = MatchState.LIVE
        self._rounds_played = 0
        self._publish(MATCH_RESTARTED_EVENT, {"difficulty": self._difficulty})

    def _assert_can_play_a_round(self) -> None:
        if self._match_state is not MatchState.LIVE:
            raise ValueError(
                f"a round cannot be played while the match is "
                f"{self._match_state.value}; play only ever starts from a "
                "live match"
            )

    def _assert_match_is_live(self, action: str) -> None:
        if self._match_state is not MatchState.LIVE:
            raise ValueError(
                f"{action} needs a live match, not a "
                f"{self._match_state.value} one"
            )

    def _settle_round(self, player_succeeded: bool) -> RoundResult:
        self._publish(ROUND_STARTED_EVENT, {"difficulty": self._difficulty})
        observation = DifficultyObservation(player_succeeded=player_succeeded)
        self._difficulty = self._difficulty_strategy.adjust(
            self._difficulty, observation
        )
        self._publish(DIFFICULTY_ADJUSTED_EVENT, {"difficulty": self._difficulty})
        self._rounds_played += 1
        return RoundResult(
            difficulty=self._difficulty, player_succeeded=player_succeeded
        )

    def _end_match_in_death(self) -> None:
        self._match_state = MatchState.DEAD
        self._publish(MATCH_ENDED_EVENT, {"difficulty": self._difficulty})

    def _publish(self, event_name: str, payload: dict[str, float]) -> None:
        self._event_publisher.publish(
            DomainEvent(name=event_name, payload=payload)
        )
