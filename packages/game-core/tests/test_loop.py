"""Loop behaviour with fake ports: reporting, delegation, and loud refusals."""

import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import pytest

from game_core import DomainEvent, GameLoop


class RecordingPublisher:
    """Fake event port that remembers everything published to it."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)


class FixedStepStrategy:
    """Fake difficulty port that moves the difficulty by a constant step."""

    def __init__(self, step: float = 0.0) -> None:
        self._step = step
        self.observed: list[object] = []

    def adjust(self, current_difficulty: float, observation: object) -> float:
        self.observed.append(observation)
        return current_difficulty + self._step


def make_loop(strategy_step: float = 0.0) -> tuple[GameLoop, RecordingPublisher, FixedStepStrategy]:
    publisher = RecordingPublisher()
    strategy = FixedStepStrategy(step=strategy_step)
    loop = GameLoop(event_publisher=publisher, difficulty_strategy=strategy)
    return loop, publisher, strategy


def test_an_unwired_event_publisher_is_refused_loudly():
    with pytest.raises(ValueError, match="event publisher"):
        GameLoop(event_publisher=None, difficulty_strategy=FixedStepStrategy())


def test_an_unwired_difficulty_strategy_is_refused_loudly():
    with pytest.raises(ValueError, match="difficulty strategy"):
        GameLoop(event_publisher=RecordingPublisher(), difficulty_strategy=None)


def test_a_fresh_loop_sits_at_the_starting_difficulty():
    loop, _, _ = make_loop()

    assert loop.difficulty == 0.5


def test_a_round_is_reported_as_started_then_adjusted():
    loop, publisher, _ = make_loop(strategy_step=0.1)

    loop.play_round(player_succeeded=True)

    event_names = [event.name for event in publisher.published]
    assert event_names == ["round.started", "difficulty.adjusted"]


def test_each_reported_event_carries_the_difficulty_in_force():
    loop, publisher, _ = make_loop(strategy_step=0.1)

    loop.play_round(player_succeeded=True)

    payloads = [event.payload["difficulty"] for event in publisher.published]
    assert payloads == [0.5, 0.6]


def test_the_round_outcome_reaches_the_strategy():
    loop, _, strategy = make_loop()

    loop.play_round(player_succeeded=True)

    (observation,) = strategy.observed
    assert observation.player_succeeded is True


def test_a_lost_round_reaches_the_strategy_as_a_failure():
    loop, _, strategy = make_loop()

    loop.play_round(player_succeeded=False)

    (observation,) = strategy.observed
    assert observation.player_succeeded is False


def test_the_loop_adopts_whatever_difficulty_the_strategy_returns():
    loop, _, _ = make_loop(strategy_step=0.1)

    result = loop.play_round(player_succeeded=True)

    assert result.difficulty == 0.6
    assert loop.difficulty == 0.6
