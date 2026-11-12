"""The adaptive difficulty policy implementing the loop's port.

This module follows the shape of the contract game-core defines without
importing it, so the modules stay independently scoped. When a future project
copies this template, the copy point is this policy: replace the rule-based
class with the project's own model and keep the method contract.
"""

from typing import Protocol

DEFAULT_STEP_SIZE = 1
DEFAULT_EASIEST_DIFFICULTY = 1
DEFAULT_HARDEST_DIFFICULTY = 10


class OutcomeShape(Protocol):
    """The outcome shape the port hands over; game-core's dataclass satisfies it."""

    @property
    def succeeded(self) -> bool:
        ...


class RuleBasedAdaptiveDifficulty:
    """Moves the difficulty one step toward an easier or harder round."""

    def __init__(
        self,
        step_size: int = DEFAULT_STEP_SIZE,
        easiest_difficulty: int = DEFAULT_EASIEST_DIFFICULTY,
        hardest_difficulty: int = DEFAULT_HARDEST_DIFFICULTY,
    ) -> None:
        self._validate(step_size, easiest_difficulty, hardest_difficulty)
        self._step_size = step_size
        self._easiest = easiest_difficulty
        self._hardest = hardest_difficulty

    def next_difficulty(self, current_difficulty: int, outcome: OutcomeShape) -> int:
        proposed = self._proposed_for(current_difficulty, outcome)
        return self._clamped(proposed)

    def _proposed_for(self, current_difficulty: int, outcome: OutcomeShape) -> int:
        if outcome.succeeded:
            return current_difficulty + self._step_size
        return current_difficulty - self._step_size

    def _clamped(self, difficulty: int) -> int:
        return min(self._hardest, max(self._easiest, difficulty))

    @staticmethod
    def _validate(
        step_size: int, easiest_difficulty: int, hardest_difficulty: int
    ) -> None:
        if step_size < 1:
            raise ValueError("step_size must move the difficulty by at least one")
        if easiest_difficulty > hardest_difficulty:
            raise ValueError(
                "easiest_difficulty must not sit above hardest_difficulty"
            )
