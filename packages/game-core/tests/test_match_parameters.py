"""The knob store: one centralized, validating configuration surface.

Every tunable the game reads -- starting difficulty, speed, board size and
obstacle count -- lives here, mutable mid-game, refusing unknown names and
invalid values loudly.
"""

import dataclasses
import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import pytest


def test_the_store_supplies_its_defaults_from_one_place():
    from game_core import MatchKnobs

    knobs = MatchKnobs()

    assert knobs.starting_difficulty == 0.5
    assert knobs.speed == 1.0
    assert knobs.board_size == 10
    assert knobs.obstacle_count == 5


def test_a_parameter_change_applies_without_code_changes():
    from game_core import MatchKnobs

    knobs = MatchKnobs(speed=1.0, board_size=10, obstacle_count=5)

    knobs.update(speed=2.5, board_size=16, obstacle_count=11)

    assert knobs.speed == 2.5
    assert knobs.board_size == 16
    assert knobs.obstacle_count == 11


def test_an_unknown_parameter_is_refused_loudly():
    from game_core import MatchKnobs

    knobs = MatchKnobs()

    with pytest.raises(ValueError, match="trickiness"):
        knobs.update(trickiness=0.9)


@pytest.mark.parametrize(
    ("offending_construction", "message_fragment"),
    [
        ({"speed": 0}, "speed"),
        ({"speed": -0.5}, "speed"),
        ({"board_size": 0}, "board_size"),
        ({"board_size": -10}, "board_size"),
        ({"obstacle_count": -1}, "obstacle_count"),
        ({"starting_difficulty": -0.1}, "starting_difficulty"),
        ({"starting_difficulty": 1.5}, "starting_difficulty"),
    ],
)
def test_construction_refuses_invalid_values_loudly(
    offending_construction, message_fragment
):
    from game_core import MatchKnobs

    with pytest.raises(ValueError, match=message_fragment):
        MatchKnobs(**offending_construction)


@pytest.mark.parametrize(
    ("offending_update", "message_fragment"),
    [
        ({"speed": 0}, "speed"),
        ({"speed": -1.0}, "speed"),
        ({"board_size": 0}, "board_size"),
        ({"obstacle_count": -2}, "obstacle_count"),
    ],
)
def test_invalid_parameter_values_are_refused_loudly(
    offending_update, message_fragment
):
    from game_core import MatchKnobs

    knobs = MatchKnobs()

    with pytest.raises(ValueError, match=message_fragment):
        knobs.update(**offending_update)


@pytest.mark.parametrize(
    ("rejected_update", "message_fragment"),
    [
        ({"board_size": 0}, "board_size"),
        ({"obstacle_count": -3}, "obstacle_count"),
        ({"speed": 0, "obstacle_count": 2}, "speed"),
    ],
)
def test_a_rejected_update_leaves_the_configuration_untouched(
    rejected_update, message_fragment
):
    from game_core import MatchKnobs

    knobs = MatchKnobs(
        starting_difficulty=0.3, speed=1.2, board_size=8, obstacle_count=2
    )
    configuration_before = dataclasses.replace(knobs)

    with pytest.raises(ValueError, match=message_fragment):
        knobs.update(**rejected_update)

    assert knobs == configuration_before
