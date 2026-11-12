"""The adaptive difficulty port: the seam isolating the AI layer.

The loop calls out through this contract; any policy the game plays with
implements it. Nothing here knows which policy is behind the port.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PlayerOutcome:
    """What happened for a player in one round."""

    succeeded: bool


class AdaptiveDifficulty(Protocol):
    """Port the game loop calls out to for the next difficulty."""

    def next_difficulty(self, current_difficulty: int, outcome: PlayerOutcome) -> int:
        """Return the difficulty the next round should play at."""
        ...
