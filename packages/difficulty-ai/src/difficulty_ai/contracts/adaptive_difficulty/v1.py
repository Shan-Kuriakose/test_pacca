"""Version 1 of the difficulty contract consumed by difficulty-ai.

Each adapter pins a byte-for-byte copy of this contract rather than importing
game-core, so the modules remain independently deployable.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DifficultyObservation:
    """What the loop learned from one finished round."""

    player_succeeded: bool


class AdaptiveDifficulty(Protocol):
    """Port the loop calls between rounds; the AI layer implements it."""

    def adjust(
        self, current_difficulty: float, observation: DifficultyObservation
    ) -> float: ...


__all__ = ["AdaptiveDifficulty", "DifficultyObservation"]
