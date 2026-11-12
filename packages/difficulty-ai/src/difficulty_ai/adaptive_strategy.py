"""The rule-based adaptive pattern: the template's default strategy.

A future project keeps the shape and swaps the rules for its own model.
Everything the strategy needs to know about the player arrives in the
observation, so the strategy never needs to know the loop.

Its tuning lives in ``DifficultyKnobs``, a mutable store read on every
adjustment, so the AI layer can retune mid-run without rewiring anything.
"""

import dataclasses
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


class MutableKnobStore:
    """Refuses unknown parameter names, then re-validates every change.

    The store validates the whole configuration, not just the values passed
    in, so a half-finished update can never be half-applied: the candidate
    KnobStore is validated before a single field moves.

    This module shares no imports with game-core, so the two knob stores each
    carry their own copy of this protocol by design.
    """

    def update(self, **parameters: object) -> None:
        unknown = set(parameters) - set(self.__dataclass_fields__)
        if unknown:
            raise ValueError(
                f"unknown parameter name(s): {', '.join(sorted(unknown))}"
            )
        candidate = dataclasses.replace(self, **parameters)
        for field in dataclasses.fields(self):
            setattr(self, field.name, getattr(candidate, field.name))


@dataclass
class DifficultyKnobs(MutableKnobStore):
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


#: Retained under its original name for the template's existing callers.
DifficultyStepSettings = DifficultyKnobs


class RuleBasedAdaptiveStrategy:
    """Implements the difficulty port with knobs read on every adjustment."""

    def __init__(
        self,
        settings: DifficultyKnobs | None = None,
        *,
        knobs: DifficultyKnobs | None = None,
    ) -> None:
        self._settings = knobs if knobs is not None else (
            settings if settings is not None else DifficultyKnobs()
        )

    def adjust(self, current_difficulty: float, observation: RoundObservation) -> float:
        """Move the difficulty one step in the direction the round implies."""
        if observation.player_succeeded:
            step = self._settings.rise_on_success
        else:
            step = -self._settings.drop_on_failure
        return self._clamped_to_bounds(current_difficulty + step)

    def _clamped_to_bounds(self, difficulty: float) -> float:
        return min(
            self._settings.maximum_difficulty,
            max(self._settings.minimum_difficulty, difficulty),
        )
