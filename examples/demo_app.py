"""The copied template's wiring demo: three modules, one running game.

Executable through examples/run_demo.py, and imported by the suite's own
test so the orchestration stays under test like any other code.
"""

import sys
from pathlib import Path

_TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
for _source_root in sorted((_TEMPLATE_ROOT / "packages").glob("*/src")):
    sys.path.insert(0, str(_source_root))

from difficulty_ai import RuleBasedAdaptiveDifficulty  # noqa: E402
from event_instrumentation import InMemoryEventSink  # noqa: E402
from game_core import GameLoop  # noqa: E402

DEMO_OUTCOMES = ("win", "win", "loss", "win", "tie", "loss")
STARTING_LEVEL = 3


def build_components():
    """Wire the three modules: the one seam a copied template touches."""
    sink = InMemoryEventSink()
    difficulty = RuleBasedAdaptiveDifficulty()
    game_loop = GameLoop(
        publisher=sink, difficulty=difficulty, starting_level=STARTING_LEVEL
    )
    return game_loop, sink


def play_demo_rounds(game_loop) -> None:
    for outcome in DEMO_OUTCOMES:
        game_loop.play_round(outcome)


def report(game_loop, sink) -> None:
    print("wired game_core.GameLoop")
    print("wired difficulty_ai.RuleBasedAdaptiveDifficulty")
    print("wired event_instrumentation.InMemoryEventSink")
    print(f"final difficulty level: {game_loop.level}")
    print(f"events published: {len(sink.events())}")


def main() -> int:
    game_loop, sink = build_components()
    play_demo_rounds(game_loop)
    report(game_loop, sink)
    return len(sink.events())
