"""difficulty-ai: the reusable adaptive pattern behind the difficulty port.

This module imports nothing from game-core. It satisfies game-core's
AdaptiveDifficulty port structurally, so the dependency between the layers
runs from the loop to its adapter and never the reverse.
"""

from difficulty_ai.adaptive_strategy import RuleBasedAdaptiveDifficulty

__all__ = ["RuleBasedAdaptiveDifficulty"]
