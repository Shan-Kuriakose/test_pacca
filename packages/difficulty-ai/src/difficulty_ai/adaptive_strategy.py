"""The rule-based adaptive pattern: the template's default strategy.

A future project keeps the shape and swaps the rules for its own model.
Everything the strategy needs to know about the player arrives in the
observation, so the strategy never needs to know the loop.
"""

from dataclasses import dataclass
from typing import Protocol


class RoundObservation(Protocol):
    """Anything that reports how the last round went.

    This mirrors the observation the loop passes, structurally: the strategy
    reads ``player_succeeded`` and nothing else, so it stays decoupled from
    the engine's types.
    """

    @property
    def player_succeeded(self) -> bool: ...


@dataclass(frozen=True)
class DifficultyStepSettings:
    """How far difficulty moves per round, and where it may sit."""

    rise_on_success: float = 0.1
    drop_on_failure: float = 0.15
    minimum_difficulty: float = 0.1
    maximum_difficulty: float = 1.0

    def __post_init__(self) -> None:
        if self.rise_on_success < 0 or self.drop_on_failure < 0:
            raise ValueError("difficulty steps must never be negative")
        if self.minimum_difficulty >= self.maximum_difficulty:
            raise ValueError("the minimum difficulty must stay below the maximum")


class RuleBasedAdaptiveStrategy:
    """Implements the difficulty port with fixed steps inside fixed bounds."""

    def __init__(self, settings: DifficultyStepSettings | None = None) -> None:
        self._settings = settings if settings is not None else DifficultyStepSettings()

    def adjust(self, current_difficulty: float, observation: RoundObservation) -> float:
        """Move the difficulty one step in the direction the round implies."""
        if observation.player_succeeded:
            step = self._settings.rise_on_success
        else:
            step = -self._settings.drop_on_failure
        return self._clamped_to_bounds(current_difficulty + step)

    def restarted_match(self, difficulty_after_death: float) -> float:
        """Retune between games: the default keeps the difficulty as it died."""
        return self._clamped_to_bounds(difficulty_after_death)

    def _clamped_to_bounds(self, difficulty: float) -> float:
        return min(
            self._settings.maximum_difficulty,
            max(self._settings.minimum_difficulty, difficulty),
        )
