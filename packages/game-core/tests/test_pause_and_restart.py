"""Pause and restart flows on the match lifecycle.

Covers AC1 (pausing a live match freezes it and resumes exactly where it
left off), AC2 (a death ends the match and restart begins a new round
immediately) and AC3 (a restart is a between-games hook the difficulty
strategy retunes through).
"""

import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import pytest

from game_core import DomainEvent, GameLoop

MATCH_ENDED_EVENT = "match.ended"
MATCH_RESTARTED_EVENT = "match.restarted"


class RecordingPublisher:
    """Fake event port that remembers everything published to it."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)


class RestartSpyStrategy:
    """Fake difficulty port that steps per round and records the restart hook."""

    def __init__(self, step: float = 0.0, restart_difficulty: float = 0.5) -> None:
        self._step = step
        self._restart_difficulty = restart_difficulty
        self.restarted_from: list[float] = []

    def adjust(self, current_difficulty: float, observation: object) -> float:
        return current_difficulty + self._step

    def restarted_match(self, difficulty_after_death: float) -> float:
        self.restarted_from.append(difficulty_after_death)
        return self._restart_difficulty


def make_loop(
    step: float = 0.0, restart_difficulty: float = 0.5
) -> tuple[GameLoop, RecordingPublisher, RestartSpyStrategy]:
    publisher = RecordingPublisher()
    strategy = RestartSpyStrategy(step=step, restart_difficulty=restart_difficulty)
    loop = GameLoop(event_publisher=publisher, difficulty_strategy=strategy)
    return loop, publisher, strategy


def published_names(publisher: RecordingPublisher) -> list[str]:
    return [event.name for event in publisher.published]


def test_pausing_a_live_match_freezes_the_difficulty_in_force():
    from game_core import MatchState

    loop, _, _ = make_loop(step=0.1)
    loop.play_round(player_succeeded=True)
    difficulty_before_pause = loop.difficulty

    loop.pause()

    assert loop.match_state is MatchState.PAUSED
    assert loop.difficulty == difficulty_before_pause


def test_a_round_cannot_be_played_while_the_match_is_paused():
    loop, _, _ = make_loop()
    loop.pause()

    with pytest.raises(ValueError):
        loop.play_round(player_succeeded=True)


def test_resuming_leaves_the_loop_exactly_where_it_paused():
    loop, _, _ = make_loop(step=0.1)
    loop.play_round(player_succeeded=True)
    loop.pause()
    frozen_difficulty = loop.difficulty

    loop.resume()

    assert loop.difficulty == frozen_difficulty
    next_round = loop.play_round(player_succeeded=True)
    assert next_round.difficulty == pytest.approx(frozen_difficulty + 0.1)


def test_double_pause_and_stray_resume_are_refused_loudly():
    loop, _, _ = make_loop()
    fresh_loop, _, _ = make_loop()

    loop.pause()
    with pytest.raises(ValueError):
        loop.pause()

    with pytest.raises(ValueError):
        fresh_loop.resume()


def test_losing_a_round_ends_the_match_in_death():
    from game_core import MatchState

    loop, publisher, _ = make_loop()

    loop.play_round(player_succeeded=False)

    assert loop.match_state is MatchState.DEAD
    assert MATCH_ENDED_EVENT in published_names(publisher)


def test_a_play_attempt_on_a_dead_match_is_refused_loudly():
    loop, _, _ = make_loop()
    loop.play_round(player_succeeded=False)

    with pytest.raises(ValueError):
        loop.play_round(player_succeeded=True)


def test_restarting_a_dead_match_begins_the_next_round_immediately():
    from game_core import MatchState

    loop, _, _ = make_loop(step=0.1, restart_difficulty=0.3)
    loop.play_round(player_succeeded=False)

    loop.restart()

    next_round = loop.play_round(player_succeeded=True)
    assert loop.match_state is not MatchState.DEAD
    assert loop.difficulty == pytest.approx(0.3)
    assert next_round.difficulty == pytest.approx(0.4)


def test_restarting_a_live_match_is_refused_loudly():
    loop, _, _ = make_loop()

    with pytest.raises(ValueError):
        loop.restart()


def test_a_restart_asks_the_strategy_to_retune_between_games():
    loop, publisher, strategy = make_loop(step=0.1, restart_difficulty=0.3)
    loop.play_round(player_succeeded=False)

    loop.restart()

    assert len(strategy.restarted_from) == 1
    assert strategy.restarted_from[0] == pytest.approx(0.6)
    assert loop.difficulty == pytest.approx(0.3)
    restarted_events = [
        event
        for event in publisher.published
        if event.name == MATCH_RESTARTED_EVENT
    ]
    assert len(restarted_events) == 1
    assert restarted_events[0].payload["difficulty"] == pytest.approx(0.3)
