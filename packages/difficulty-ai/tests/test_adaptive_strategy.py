"""Behaviour of the adaptive strategy, including its refusal paths."""

import pytest

from difficulty_ai import RuleBasedAdaptiveDifficulty

STARTING_DIFFICULTY = 5


class FakeOutcome:
    """Stands in for the outcome dataclass game-core supplies through the port."""

    def __init__(self, succeeded: bool) -> None:
        self.succeeded = succeeded


def test_a_win_proposes_one_step_harder():
    strategy = RuleBasedAdaptiveDifficulty()

    assert (
        strategy.next_difficulty(STARTING_DIFFICULTY, FakeOutcome(True))
        == STARTING_DIFFICULTY + 1
    )


def test_a_loss_proposes_one_step_easier():
    strategy = RuleBasedAdaptiveDifficulty()

    assert (
        strategy.next_difficulty(STARTING_DIFFICULTY, FakeOutcome(False))
        == STARTING_DIFFICULTY - 1
    )


def test_a_win_never_proposes_above_the_hardest_difficulty():
    strategy = RuleBasedAdaptiveDifficulty(hardest_difficulty=STARTING_DIFFICULTY)

    assert (
        strategy.next_difficulty(STARTING_DIFFICULTY, FakeOutcome(True))
        == STARTING_DIFFICULTY
    )


def test_a_loss_never_proposes_below_the_easiest_difficulty():
    strategy = RuleBasedAdaptiveDifficulty(easiest_difficulty=STARTING_DIFFICULTY)

    assert (
        strategy.next_difficulty(STARTING_DIFFICULTY, FakeOutcome(False))
        == STARTING_DIFFICULTY
    )


def test_step_size_configures_how_far_a_round_moves_the_difficulty():
    strategy = RuleBasedAdaptiveDifficulty(step_size=2)

    assert (
        strategy.next_difficulty(STARTING_DIFFICULTY, FakeOutcome(True))
        == STARTING_DIFFICULTY + 2
    )


def test_a_non_moving_step_size_is_refused():
    with pytest.raises(ValueError):
        RuleBasedAdaptiveDifficulty(step_size=0)


def test_an_inverted_difficulty_range_is_refused():
    with pytest.raises(ValueError):
        RuleBasedAdaptiveDifficulty(easiest_difficulty=10, hardest_difficulty=1)
