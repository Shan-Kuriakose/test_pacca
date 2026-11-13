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


def an_unstarted_loop() -> GameLoop:
    """A loop wired with fake ports, with no match running yet."""
    return GameLoop(event_publisher=RecordingPublisher(), difficulty_strategy=FixedStepStrategy())


def make_loop(strategy_step: float = 0.0) -> tuple[GameLoop, RecordingPublisher, FixedStepStrategy]:
    """Wire a loop with fake ports and start the match it plays rounds in."""
    publisher = RecordingPublisher()
    strategy = FixedStepStrategy(step=strategy_step)
    loop = GameLoop(event_publisher=publisher, difficulty_strategy=strategy)
    loop.start_match()
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


def test_playing_a_round_without_a_started_match_is_refused_loudly():
    loop = an_unstarted_loop()

    with pytest.raises(ValueError, match="no match is running"):
        loop.play_round(player_succeeded=True)


def test_ending_a_match_without_one_in_progress_is_refused_loudly():
    loop = an_unstarted_loop()

    with pytest.raises(ValueError, match="no match is in progress to end"):
        loop.end_match()


def test_starting_a_second_match_while_one_runs_is_refused_loudly():
    loop, _, _ = make_loop()

    with pytest.raises(ValueError, match="a match is already in progress"):
        loop.start_match()


def test_a_round_is_reported_as_started_then_adjusted():
    loop, publisher, _ = make_loop(strategy_step=0.1)

    loop.play_round(player_succeeded=True)

    event_names = [event.name for event in publisher.published]
    assert event_names == ["match.started", "round.started", "difficulty.adjusted"]


def test_each_reported_event_carries_the_difficulty_in_force():
    loop, publisher, _ = make_loop(strategy_step=0.1)

    loop.play_round(player_succeeded=True)

    payloads = [
        event.payload["difficulty"]
        for event in publisher.published
        if "difficulty" in event.payload
    ]
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


def test_each_new_match_reads_its_parameters_from_the_store():
    from game_core import MatchKnobs

    knobs = MatchKnobs(
        starting_difficulty=0.7, speed=1.5, board_size=12, obstacle_count=4
    )
    publisher = RecordingPublisher()
    loop = GameLoop(
        event_publisher=publisher,
        difficulty_strategy=FixedStepStrategy(),
        knobs=knobs,
    )

    loop.start_match()

    (match_started,) = [
        event for event in publisher.published if event.name == "match.started"
    ]
    assert match_started.payload == {
        "starting_difficulty": 0.7,
        "speed": 1.5,
        "board_size": 12,
        "obstacle_count": 4,
    }
    assert loop.difficulty == 0.7

    knobs.update(board_size=20)
    publisher.published.clear()
    loop.end_match()
    loop.start_match()

    (second_match,) = [
        event for event in publisher.published if event.name == "match.started"
    ]
    assert second_match.payload["board_size"] == 20


def test_a_midgame_knob_update_reaches_the_next_round():
    from game_core import MatchKnobs

    knobs = MatchKnobs(speed=1.0)
    publisher = RecordingPublisher()
    loop = GameLoop(
        event_publisher=publisher,
        difficulty_strategy=FixedStepStrategy(),
        knobs=knobs,
    )

    loop.start_match()
    loop.play_round(player_succeeded=True)
    knobs.update(speed=3.0)
    loop.play_round(player_succeeded=True)

    round_started_payloads = [
        event.payload
        for event in publisher.published
        if event.name == "round.started"
    ]
    assert round_started_payloads[0]["speed"] == 1.0
    assert round_started_payloads[1]["speed"] == 3.0


def test_a_midgame_starting_difficulty_update_waits_for_the_next_match():
    from game_core import MatchKnobs

    knobs = MatchKnobs(starting_difficulty=0.5)
    publisher = RecordingPublisher()
    loop = GameLoop(
        event_publisher=publisher,
        difficulty_strategy=FixedStepStrategy(),
        knobs=knobs,
    )

    loop.start_match()
    loop.play_round(player_succeeded=True)
    knobs.update(starting_difficulty=0.8, speed=2.0)

    assert loop.difficulty == 0.5, (
        "a starting_difficulty change mid-match may not disturb the "
        "difficulty the running match is already playing at"
    )

    loop.end_match()
    loop.start_match()

    (second_match_started,) = [
        event for event in publisher.published if event.name == "match.started"
    ][1:]
    assert second_match_started.payload["starting_difficulty"] == 0.8
    assert second_match_started.payload["speed"] == 2.0
    assert loop.difficulty == 0.8
