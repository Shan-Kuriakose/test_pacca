"""Executable proof of the template: wire the three modules and play.

Run from a clean checkout with ``python examples/run_demo.py``. The script
wires the loop (game-core) to the rule-based strategy (difficulty-ai) and the
in-memory sink (event-instrumentation), plays a few rounds, and reports what
was recorded -- with no network access and no credentials.

A future project copies the repository and replaces exactly two things: the
rules inside difficulty-ai, and the sink inside event-instrumentation.
"""

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_ROOT = REPOSITORY_ROOT / "packages"
ROUNDS_TO_PLAY = (True, True, False, True)


def make_module_sources_importable() -> None:
    """Put each module's src directory on the import path."""
    for source_root in sorted(PACKAGES_ROOT.glob("*/src")):
        sys.path.insert(0, str(source_root))


def wire_the_template() -> tuple[object, object]:
    """Connect the loop to its two adapters, outside of game-core."""
    from difficulty_ai import RuleBasedAdaptiveStrategy
    from event_instrumentation import InMemoryEventSink
    from game_core import GameLoop

    sink = InMemoryEventSink()
    strategy = RuleBasedAdaptiveStrategy()
    loop = GameLoop(event_publisher=sink, difficulty_strategy=strategy)
    return loop, sink


def play_demo_rounds(loop: object) -> None:
    """Play the scripted rounds so the loop adjusts the difficulty."""
    for player_succeeded in ROUNDS_TO_PLAY:
        loop.play_round(player_succeeded=player_succeeded)


def report_the_run(loop: object, sink: object) -> None:
    """Print what was wired and what the run produced."""
    print("wired game_core.GameLoop")
    print("  difficulty strategy <- difficulty_ai.RuleBasedAdaptiveStrategy")
    print("  event publisher     <- event_instrumentation.InMemoryEventSink")
    print(f"final difficulty after {len(ROUNDS_TO_PLAY)} rounds: {loop.difficulty:.2f}")
    print(f"events recorded by the sink: {len(sink.events())}")


def main() -> int:
    make_module_sources_importable()
    loop, sink = wire_the_template()
    play_demo_rounds(loop)
    report_the_run(loop, sink)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
