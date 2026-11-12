"""Strategy behaviour: movement per round, boundary clamping, loud settings."""

import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import dataclasses

import pytest

import difficulty_ai
from difficulty_ai import DifficultyStepSettings, RuleBasedAdaptiveStrategy


def make_strategy(**overrides) -> RuleBasedAdaptiveStrategy:
    settings = DifficultyStepSettings(**overrides)
    return RuleBasedAdaptiveStrategy(settings=settings)


@dataclasses.dataclass(frozen=True)
class Outcome:
    """A stand-in observation, shaped like the one the loop passes."""

    player_succeeded: bool


def test_a_won_round_rises_the_difficulty():
    strategy = make_strategy()

    adjusted = strategy.adjust(0.5, Outcome(player_succeeded=True))

    assert adjusted == pytest.approx(0.6)


def test_a_lost_round_drops_the_difficulty():
    strategy = make_strategy()

    adjusted = strategy.adjust(0.5, Outcome(player_succeeded=False))

    assert adjusted == pytest.approx(0.35)


def test_repeated_wins_never_exceed_the_maximum():
    strategy = make_strategy()

    difficulty = 0.5
    for _ in range(10):
        difficulty = strategy.adjust(difficulty, Outcome(player_succeeded=True))

    assert difficulty == pytest.approx(1.0)


def test_repeated_losses_never_fall_below_the_minimum():
    strategy = make_strategy()

    difficulty = 0.5
    for _ in range(10):
        difficulty = strategy.adjust(difficulty, Outcome(player_succeeded=False))

    assert difficulty == pytest.approx(0.1)


def test_the_adjusted_difficulty_always_stays_within_the_bounds():
    strategy = make_strategy()

    difficulty = 0.5
    for succeeded in [True, True, False, False, True, False]:
        difficulty = strategy.adjust(difficulty, Outcome(player_succeeded=succeeded))
        assert strategy_bounds_contain(strategy, difficulty)


def strategy_bounds_contain(strategy: RuleBasedAdaptiveStrategy, candidate: float) -> bool:
    settings = strategy._settings
    return settings.minimum_difficulty <= candidate <= settings.maximum_difficulty


def test_a_strategy_starts_at_its_settings_bounds():
    strategy = make_strategy(minimum_difficulty=0.2, maximum_difficulty=0.8)

    adjusted = strategy.adjust(0.8, Outcome(player_succeeded=True))

    assert adjusted == pytest.approx(0.8)


def test_negative_steps_are_refused_loudly():
    with pytest.raises(ValueError, match="steps must never be negative"):
        make_strategy(rise_on_success=-0.1)


def test_an_inverted_range_is_refused_loudly():
    with pytest.raises(ValueError, match="minimum difficulty must stay below"):
        make_strategy(minimum_difficulty=0.9, maximum_difficulty=0.2)


def test_the_module_publishes_its_public_surface():
    assert "RuleBasedAdaptiveStrategy" in difficulty_ai.__all__
    assert "DifficultyStepSettings" in difficulty_ai.__all__


def test_a_strategy_reads_its_knobs_on_every_adjustment():
    from difficulty_ai import DifficultyKnobs, RuleBasedAdaptiveStrategy

    knobs = DifficultyKnobs(rise_on_success=0.2)
    strategy = RuleBasedAdaptiveStrategy(knobs=knobs)

    first = strategy.adjust(0.5, Outcome(player_succeeded=True))

    knobs.update(rise_on_success=0.05)

    second = strategy.adjust(0.5, Outcome(player_succeeded=True))

    assert first == pytest.approx(0.7)
    assert second == pytest.approx(0.55)


def test_a_mid_run_knob_update_changes_the_strategy_without_rewiring():
    from difficulty_ai import DifficultyKnobs, RuleBasedAdaptiveStrategy

    knobs = DifficultyKnobs()
    strategy = RuleBasedAdaptiveStrategy(knobs=knobs)

    first = strategy.adjust(0.8, Outcome(player_succeeded=False))

    knobs.update(drop_on_failure=0.05)

    second = strategy.adjust(0.8, Outcome(player_succeeded=False))

    assert first == pytest.approx(0.65)
    assert second == pytest.approx(0.75)


def test_a_knob_update_refuses_unknown_parameters_loudly():
    from difficulty_ai import DifficultyKnobs

    knobs = DifficultyKnobs()

    with pytest.raises(ValueError, match="suddenness"):
        knobs.update(suddenness=0.4)
