"""Executable proof of the template: wire the three modules and play.

Run from a clean checkout with ``python examples/run_demo.py``. The script
wires the loop (game-core) to the rule-based strategy (difficulty-ai) and the
in-memory sink (event-instrumentation), plays a match, retunes both knob
stores through the knob interface mid-match and between matches, plays on,
and reports what was recorded -- with no network access and no credentials.

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


def wire_the_template() -> tuple[object, object, object, object]:
    """Connect the loop to its adapters and knob stores, outside game-core."""
    from difficulty_ai import DifficultyKnobs, RuleBasedAdaptiveStrategy
    from event_instrumentation import InMemoryEventSink
    from game_core import GameLoop, MatchKnobs

    sink = InMemoryEventSink()
    difficulty_knobs = DifficultyKnobs()
    strategy = RuleBasedAdaptiveStrategy(difficulty_knobs)
    match_knobs = MatchKnobs()
    loop = GameLoop(
        event_publisher=sink, difficulty_strategy=strategy, knobs=match_knobs
    )
    return loop, sink, match_knobs, difficulty_knobs


def play_demo_rounds(loop: object) -> None:
    """Play one match: start it, play the scripted rounds, end it."""
    loop.start_match()
    for player_succeeded in ROUNDS_TO_PLAY:
        loop.play_round(player_succeeded=player_succeeded)
    loop.end_match()


def tune_the_knobs(loop: object, match_knobs: object, difficulty_knobs: object) -> None:
    """Show mid-game and between-games tuning through the knob interface."""
    loop.start_match()
    difficulty_knobs.update(rise_on_success=0.2)
    loop.play_round(player_succeeded=True)
    match_knobs.update(speed=2.0, board_size=14)
    loop.end_match()
    loop.start_match()
    loop.play_round(player_succeeded=True)
    loop.end_match()


def count_rounds_played(sink: object) -> int:
    """Count the rounds the sink recorded, from round.started events."""
    return len(sink.events_named("round.started"))


def report_the_run(loop: object, sink: object) -> None:
    """Print what was wired and what the run produced."""
    print("wired game_core.GameLoop")
    print("  difficulty strategy <- difficulty_ai.RuleBasedAdaptiveStrategy")
    print("  event publisher     <- event_instrumentation.InMemoryEventSink")
    print(
        f"final difficulty after {count_rounds_played(sink)} rounds: "
        f"{loop.difficulty:.2f}"
    )
    print(f"events recorded by the sink: {len(sink.events())}")


def main() -> int:
    make_module_sources_importable()
    loop, sink, match_knobs, difficulty_knobs = wire_the_template()
    play_demo_rounds(loop)
    tune_the_knobs(loop, match_knobs, difficulty_knobs)
    report_the_run(loop, sink)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
