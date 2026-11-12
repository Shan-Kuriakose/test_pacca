"""The knob store: one centralized, validating configuration surface.

Every tunable the game reads -- starting difficulty, speed, board size and
obstacle count -- lives here, mutable mid-game, refusing unknown names and
invalid values loudly.
"""

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
