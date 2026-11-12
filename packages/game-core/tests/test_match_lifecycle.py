"""The match lifecycle: rounds only ever run inside a started match."""

import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import pytest

from game_core import DomainEvent, GameLoop, MatchKnobs


class RecordingPublisher:
    """Fake event port that remembers everything published to it."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)


class ConstantStepStrategy:
    """Fake difficulty port that moves the difficulty by a constant step."""

    def __init__(self, step: float = 0.0) -> None:
        self._step = step

    def adjust(self, current_difficulty: float, observation: object) -> float:
        return current_difficulty + self._step


def make_started_loop(
    knobs: MatchKnobs | None = None,
) -> tuple[GameLoop, RecordingPublisher]:
    """Build a loop whose match has started, with a recording publisher."""
    publisher = RecordingPublisher()
    loop = GameLoop(
        event_publisher=publisher,
        difficulty_strategy=ConstantStepStrategy(),
        knobs=knobs,
    )
    loop.start_match()
    return loop, publisher


def test_a_round_before_any_match_started_is_refused_loudly():
    publisher = RecordingPublisher()
    loop = GameLoop(
        event_publisher=publisher, difficulty_strategy=ConstantStepStrategy()
    )

    with pytest.raises(ValueError, match="no match is in progress"):
        loop.play_round(player_succeeded=True)


def test_no_round_event_escapes_a_refused_round():
    publisher = RecordingPublisher()
    loop = GameLoop(
        event_publisher=publisher, difficulty_strategy=ConstantStepStrategy()
    )

    with pytest.raises(ValueError, match="no match is in progress"):
        loop.play_round(player_succeeded=True)

    assert publisher.published == []


def test_a_match_that_has_played_refuses_a_new_start_until_finished():
    loop, _ = make_started_loop()
    loop.play_round(player_succeeded=True)

    with pytest.raises(ValueError, match="already in progress"):
        loop.start_match()


def test_finishing_a_match_opens_the_between_games_boundary():
    knobs = MatchKnobs(board_size=10)
    loop, publisher = make_started_loop(knobs=knobs)
    loop.play_round(player_succeeded=True)
    loop.finish_match()

    knobs.update(board_size=18)
    loop.start_match()

    latest_match = publisher.published[-1]
    assert latest_match.name == "match.started"
    assert latest_match.payload["board_size"] == 18


def test_finishing_without_a_match_in_progress_is_refused_loudly():
    publisher = RecordingPublisher()
    loop = GameLoop(
        event_publisher=publisher, difficulty_strategy=ConstantStepStrategy()
    )

    with pytest.raises(ValueError, match="no match is in progress"):
        loop.finish_match()


def test_a_match_before_its_first_round_reads_a_freshly_tuned_store():
    knobs = MatchKnobs(speed=1.0)
    loop, publisher = make_started_loop(knobs=knobs)

    knobs.update(speed=2.0)
    loop.start_match()

    latest_match = publisher.published[-1]
    assert latest_match.name == "match.started"
    assert latest_match.payload["speed"] == 2.0
