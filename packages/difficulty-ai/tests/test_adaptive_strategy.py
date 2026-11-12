"""RuleBasedAdaptiveDifficulty: wins, losses, boundaries and refusals."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from difficulty_ai.adaptive_strategy import (  # noqa: E402
    MAXIMUM_LEVEL,
    MINIMUM_LEVEL,
    RuleBasedAdaptiveDifficulty,
)


def test_a_win_raises_the_level_by_one_step():
    strategy = RuleBasedAdaptiveDifficulty()

    assert strategy.next_level(3, "win") == 4


def test_a_loss_lowers_the_level_by_one_step():
    strategy = RuleBasedAdaptiveDifficulty()

    assert strategy.next_level(3, "loss") == 2


def test_an_unknown_outcome_holds_the_level_steady():
    strategy = RuleBasedAdaptiveDifficulty()

    assert strategy.next_level(3, "forfeit") == 3


def test_a_win_at_the_ceiling_stays_at_the_maximum():
    strategy = RuleBasedAdaptiveDifficulty()

    assert strategy.next_level(MAXIMUM_LEVEL, "win") == MAXIMUM_LEVEL


def test_a_loss_at_the_floor_stays_at_the_minimum():
    strategy = RuleBasedAdaptiveDifficulty()

    assert strategy.next_level(MINIMUM_LEVEL, "loss") == MINIMUM_LEVEL


def test_the_strategy_stays_inside_custom_bounds():
    strategy = RuleBasedAdaptiveDifficulty(minimum_level=5, maximum_level=6)

    assert strategy.next_level(6, "win") == 6
    assert strategy.next_level(5, "loss") == 5


def test_an_inverted_bounds_configuration_fails_loudly():
    with pytest.raises(ValueError, match="minimum_level"):
        RuleBasedAdaptiveDifficulty(minimum_level=8, maximum_level=2)
