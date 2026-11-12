"""The difficulty port: the seam that keeps the AI layer out of the loop.

The loop reports how a round went and asks for the next difficulty. Which
rule, heuristic or model produces that number is a detail of the adapter,
never of the loop.
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
