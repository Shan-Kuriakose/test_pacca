"""Refusals the knob store's documented validation contract promises.

The README commits ``update()`` to refusing any invalid value with a loud
``ValueError`` naming the knob; these tests pin the invalid values that slip
past an ordinary comparison check: values that are not numbers at all,
not-a-number, infinity, and whole-number knobs given fractional values.
"""

import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import pytest


def test_a_non_numeric_value_is_refused_as_a_valueerror_naming_the_knob():
    from game_core import MatchKnobs

    knobs = MatchKnobs()

    with pytest.raises(ValueError, match="speed"):
        knobs.update(speed="fast")


def test_a_whole_number_knob_refuses_a_fractional_value():
    from game_core import MatchKnobs

    knobs = MatchKnobs()

    with pytest.raises(ValueError, match="board_size"):
        knobs.update(board_size=10.5)


@pytest.mark.parametrize(
    ("offending_update", "message_fragment"),
    [
        ({"starting_difficulty": float("nan")}, "starting_difficulty"),
        ({"speed": float("nan")}, "speed"),
        ({"board_size": float("nan")}, "board_size"),
        ({"obstacle_count": float("nan")}, "obstacle_count"),
        ({"speed": float("inf")}, "speed"),
    ],
)
def test_a_knob_that_is_not_a_finite_number_is_refused_loudly(
    offending_update, message_fragment
):
    from game_core import MatchKnobs

    knobs = MatchKnobs()

    with pytest.raises(ValueError, match=message_fragment):
        knobs.update(**offending_update)


def test_a_refused_update_leaves_every_knob_unmoved():
    from game_core import MatchKnobs

    knobs = MatchKnobs()

    with pytest.raises(ValueError):
        knobs.update(speed=float("nan"), board_size=20, obstacle_count=9)

    assert knobs.speed == 1.0
    assert knobs.board_size == 10
    assert knobs.obstacle_count == 5
