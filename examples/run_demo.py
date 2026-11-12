#!/usr/bin/env python
"""The template's runnable proof: wire all three modules and play rounds.

Run from the repository root with::

    python examples/run_demo.py

It needs no network, no credentials and no installation. When a future
project copies the template, the only swap is the difficulty policy: change
``RuleBasedAdaptiveDifficulty`` here for the project's own model and the
script otherwise reads exactly as it does now.
"""

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIRECTORIES = ("game-core", "difficulty-ai", "event-instrumentation")

ROUNDS_PASSED = (True, True, False)


def put_modules_on_path() -> None:
    """Point at each module's own source; installing the packages removes this."""
    for module_directory in MODULE_DIRECTORIES:
        source_root = REPOSITORY_ROOT / "packages" / module_directory / "src"
        sys.path.insert(0, str(source_root))


put_modules_on_path()

from difficulty_ai import RuleBasedAdaptiveDifficulty  # noqa: E402
from event_instrumentation import InMemoryEventSink  # noqa: E402
from game_core import GameLoop, PlayerOutcome  # noqa: E402


def play_rounds(game_loop: GameLoop) -> None:
    for succeeded in ROUNDS_PASSED:
        report = game_loop.run_round(PlayerOutcome(succeeded=succeeded))
        played = (
            f"round {report.round_number} at difficulty {report.difficulty}: "
            f"{'won' if report.outcome.succeeded else 'lost'}"
        )
        print(played)


def show_recorded_events(event_sink: InMemoryEventSink) -> None:
    for event in event_sink.events():
        print(f"{event.topic}: {dict(event.payload)}")


def main() -> None:
    print("wiring game_core, difficulty_ai and event_instrumentation")
    event_sink = InMemoryEventSink()
    difficulty_strategy = RuleBasedAdaptiveDifficulty()
    game_loop = GameLoop(
        event_publisher=event_sink,
        difficulty_strategy=difficulty_strategy,
    )
    play_rounds(game_loop)
    show_recorded_events(event_sink)
    print("done: difficulty_ai adapted the difficulty; event_instrumentation recorded the rounds")


if __name__ == "__main__":
    main()
