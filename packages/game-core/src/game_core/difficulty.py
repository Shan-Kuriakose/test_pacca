"""The AdaptiveDifficulty port: the seam that isolates the AI layer."""

from abc import ABC, abstractmethod


class AdaptiveDifficulty(ABC):
    """Port the loop calls out to whenever a round ends."""

    @abstractmethod
    def next_level(self, current_level: int, outcome: str) -> int:
        """Return the level to run after `outcome` at `current_level`."""
