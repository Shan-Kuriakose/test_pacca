"""The rule-based adaptive strategy: the pattern a future project swaps.

This class is the template's documented adaptive-pattern placeholder. Replace
it with a model or policy of your own; anything answering
``next_level(current_level, outcome) -> int`` inside the configured bounds
plugs straight into game-core's loop.
"""

MINIMUM_LEVEL = 1
MAXIMUM_LEVEL = 10
WIN_OUTCOME = "win"
LOSS_OUTCOME = "loss"
DIFFICULTY_STEP = 1


class RuleBasedAdaptiveDifficulty:
    """Raise the level on a win, lower it on a loss, keep it inside bounds."""

    def __init__(
        self,
        minimum_level: int = MINIMUM_LEVEL,
        maximum_level: int = MAXIMUM_LEVEL,
    ) -> None:
        if minimum_level >= maximum_level:
            raise ValueError("minimum_level must be below maximum_level.")
        self._minimum = minimum_level
        self._maximum = maximum_level

    def next_level(self, current_level: int, outcome: str) -> int:
        if outcome == WIN_OUTCOME:
            return self._clamped(current_level + DIFFICULTY_STEP)
        if outcome == LOSS_OUTCOME:
            return self._clamped(current_level - DIFFICULTY_STEP)
        return self._clamped(current_level)

    def _clamped(self, level: int) -> int:
        return min(self._maximum, max(self._minimum, level))
