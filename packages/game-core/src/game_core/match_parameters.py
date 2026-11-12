"""The centralized knob store: one configuration surface for every tunable.

The game refuses no change the store offers it -- speed, board size and
obstacle count are read from here on every match and every round, so the AI
layer can tune them mid-game and between games without touching the loop.
"""

import dataclasses
from dataclasses import dataclass


class MutableKnobStore:
    """Refuses unknown parameter names, then re-validates every change.

    The store validates the whole configuration, not just the values passed
    in, so a half-finished update can never be half-applied: the candidate
    KnobStore is validated before a single field moves.
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
class MatchKnobs(MutableKnobStore):
    """Every tunable the loop reads, mutable so tuning needs no code change."""

    starting_difficulty: float = 0.5
    speed: float = 1.0
    board_size: int = 10
    obstacle_count: int = 5

    def __post_init__(self) -> None:
        if self.speed <= 0:
            raise ValueError("speed must be positive")
        if self.board_size <= 0:
            raise ValueError("board_size must be positive")
        if self.obstacle_count < 0:
            raise ValueError("obstacle_count must never be negative")
        if not 0 <= self.starting_difficulty <= 1:
            raise ValueError("starting_difficulty must sit within [0, 1]")
