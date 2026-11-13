"""The difficulty port: the seam that keeps the AI layer out of the loop.

The loop reports how a round went and asks for the next difficulty. Which
rule, heuristic or model produces that number is a detail of the adapter,
never of the loop. The contract itself stays in a versioned file that
adapters can pin exactly.
"""

from game_core.contracts.adaptive_difficulty.v1 import (
    AdaptiveDifficulty,
    DifficultyObservation,
)

__all__ = ["AdaptiveDifficulty", "DifficultyObservation"]
