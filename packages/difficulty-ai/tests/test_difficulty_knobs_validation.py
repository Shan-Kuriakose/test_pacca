"""Refusals ``DifficultyKnobs.update()`` promises against non-numeric values.

The README commits both knob stores to refusing any invalid value with a
loud ``ValueError`` naming the knob; these tests pin the values that slip
past an ordinary bound check on the strategy's knobs.
"""

import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import pytest


def test_a_non_numeric_knob_is_refused_as_a_valueerror_naming_the_knob():
    from difficulty_ai import DifficultyKnobs

    knobs = DifficultyKnobs()

    with pytest.raises(ValueError, match="rise_on_success"):
        knobs.update(rise_on_success="steep")


@pytest.mark.parametrize(
    ("offending_update", "message_fragment"),
    [
        ({"rise_on_success": float("nan")}, "rise_on_success"),
        ({"drop_on_failure": float("nan")}, "drop_on_failure"),
        ({"minimum_difficulty": float("nan")}, "minimum_difficulty"),
        ({"maximum_difficulty": float("nan")}, "maximum_difficulty"),
        ({"maximum_difficulty": float("inf")}, "maximum_difficulty"),
    ],
)
def test_a_knob_that_is_not_a_finite_number_is_refused_loudly(
    offending_update, message_fragment
):
    from difficulty_ai import DifficultyKnobs

    knobs = DifficultyKnobs()

    with pytest.raises(ValueError, match=message_fragment):
        knobs.update(**offending_update)
