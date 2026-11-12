"""Behaviour of the round loop, with fake ports standing in for the adapters."""

import pytest

from game_core import (
    DIFFICULTY_ADJUSTED_TOPIC,
    ROUND_COMPLETED_TOPIC,
    DIFFICULTY_FLOOR,
    GameLoop,
    MissingIntegrationError,
    PlayerOutcome,
)

STARTING_DIFFICULTY = 3


class FakeEventPublisher:
    """Records what the loop emits, without any storage of its own."""

    def __init__(self) -> None:
        self.published_events = []

    def publish(self, event) -> None:
        self.published_events.append(event)


class FakeDifficultyStrategy:
    """Answers the port with whatever difficulty it was told in advance."""

    def __init__(self, next_difficulty: int) -> None:
        self._next_difficulty = next_difficulty
        self.times_consulted = 0

    def next_difficulty(self, current_difficulty: int, outcome) -> int:
        self.times_consulted += 1
        return self._next_difficulty


def built_loop(difficulty_strategy, event_publisher=None):
    publisher = (
        event_publisher if event_publisher is not None else FakeEventPublisher()
    )
    game_loop = GameLoop(
        event_publisher=publisher,
        difficulty_strategy=difficulty_strategy,
        starting_difficulty=STARTING_DIFFICULTY,
    )
    return game_loop, publisher


def test_round_completion_publishes_event_with_round_facts():
    game_loop, publisher = built_loop(FakeDifficultyStrategy(STARTING_DIFFICULTY))

    report = game_loop.run_round(PlayerOutcome(succeeded=True))

    completion_events = [
        event
        for event in publisher.published_events
        if event.topic == ROUND_COMPLETED_TOPIC
    ]
    assert len(completion_events) == 1
    assert completion_events[0].payload == {
        "round": 1,
        "difficulty": STARTING_DIFFICULTY,
        "succeeded": True,
    }
    assert report.round_number == 1
    assert report.difficulty == STARTING_DIFFICULTY


def test_round_number_increments_across_rounds():
    game_loop, publisher = built_loop(FakeDifficultyStrategy(STARTING_DIFFICULTY))

    game_loop.run_round(PlayerOutcome(succeeded=False))
    second_report = game_loop.run_round(PlayerOutcome(succeeded=False))
    game_loop.run_round(PlayerOutcome(succeeded=True))

    rounds_reported = [
        event.payload["round"]
        for event in publisher.published_events
        if event.topic == ROUND_COMPLETED_TOPIC
    ]
    assert rounds_reported == [1, 2, 3]
    assert second_report.round_number == 2


def test_difficulty_changed_by_strategy_publishes_adjustment_event():
    harder = STARTING_DIFFICULTY + 1
    game_loop, publisher = built_loop(FakeDifficultyStrategy(harder))

    game_loop.run_round(PlayerOutcome(succeeded=True))

    adjustments = [
        event
        for event in publisher.published_events
        if event.topic == DIFFICULTY_ADJUSTED_TOPIC
    ]
    assert adjustments[0].payload == {
        "round": 1,
        "from": STARTING_DIFFICULTY,
        "to": harder,
    }
    assert game_loop.difficulty == harder


def test_difficulty_held_by_strategy_publishes_no_adjustment_event():
    game_loop, publisher = built_loop(FakeDifficultyStrategy(STARTING_DIFFICULTY))

    game_loop.run_round(PlayerOutcome(succeeded=False))

    adjustments = [
        event
        for event in publisher.published_events
        if event.topic == DIFFICULTY_ADJUSTED_TOPIC
    ]
    assert adjustments == []
    assert game_loop.difficulty == STARTING_DIFFICULTY


def test_strategy_is_consulted_with_current_difficulty_and_outcome():
    class RecordingStrategy:
        def __init__(self) -> None:
            self.consulted_with = None

        def next_difficulty(self, current_difficulty, outcome):
            self.consulted_with = (current_difficulty, outcome)
            return current_difficulty

    strategy = RecordingStrategy()
    game_loop, _ = built_loop(strategy)
    outcome = PlayerOutcome(succeeded=True)

    game_loop.run_round(outcome)

    assert strategy.consulted_with == (STARTING_DIFFICULTY, outcome)


def test_loop_starts_at_the_difficulty_floor_by_default():
    game_loop = GameLoop(
        event_publisher=FakeEventPublisher(),
        difficulty_strategy=FakeDifficultyStrategy(DIFFICULTY_FLOOR),
    )

    assert game_loop.difficulty == DIFFICULTY_FLOOR


def test_missing_event_publisher_raises_loudly():
    with pytest.raises(MissingIntegrationError) as raised:
        GameLoop(event_publisher=None, difficulty_strategy=FakeDifficultyStrategy(1))

    assert "event publisher" in str(raised.value)


def test_missing_difficulty_strategy_raises_loudly():
    with pytest.raises(MissingIntegrationError) as raised:
        GameLoop(event_publisher=FakeEventPublisher(), difficulty_strategy=None)

    assert "difficulty strategy" in str(raised.value)
