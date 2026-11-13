"""The core snake game loop: a tick-based engine beside the round loop.

These are the acceptance tests for the core-snake-game-loop story (ITS-3).
AC labels here belong to that story, not to the scaffold stories whose tests
carry the same labels elsewhere in the repository.

Pinned surface, as planned: ``SnakeEngine`` starts a match by pinning a
board from ``MatchKnobs.board_size`` and a snake heading right; ``advance()``
moves one cell per tick, grows and scores on apples (``apple.eaten`` event),
and ends the run on wall or self collision with a ``RunResult`` and a
``run.finished`` event. Speed is pinned as ticks per second. A 180-degree
reversal is refused, and every tunable is read from the knob store.
"""

import sys
from pathlib import Path

_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

import pytest

from game_core import DomainEvent, MatchKnobs


class RecordingPublisher:
    """Fake event port that remembers everything published to it."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)

    def events_named(self, name: str) -> list[DomainEvent]:
        """Every published event carrying the given name, in order."""
        return [event for event in self.published if event.name == name]


class ScriptedAppleSpot:
    """Fake apple port: places each new apple one cell right of the head.

    The engine asks the port whenever the board needs an apple -- at match
    start and again after each one is eaten -- so a snake advancing right
    collects the apple on the very next tick, deterministically.
    """

    def __init__(self) -> None:
        self.requested: list[tuple] = []

    def next_apple(self, board_size: int, snake_cells) -> tuple[int, int]:
        self.requested.append((board_size, tuple(snake_cells)))
        head_row, head_column = snake_cells[0]
        return (head_row, head_column + 1)


def as_cells(cells) -> tuple[tuple[int, int], ...]:
    """The snake's cells as plain (row, column) tuples, however they come."""
    return tuple((cell[0], cell[1]) for cell in cells)


def make_engine(knobs: MatchKnobs | None = None):
    """A snake engine wired with fake ports, and the publisher it reports to."""
    from game_core import SnakeEngine

    publisher = RecordingPublisher()
    engine = SnakeEngine(
        event_publisher=publisher,
        apples=ScriptedAppleSpot(),
        knobs=knobs,
    )
    return engine, publisher


def crash_into_the_wall(engine):
    """Drive the snake straight up until the next tick leaves the board."""
    from game_core import Direction

    head_row, head_column = engine.snake_cells[0]
    for _ in range(head_row):
        engine.advance(Direction.UP)
    return engine.advance(Direction.UP)


def test_collecting_an_apple_grows_the_snake_and_increments_the_score():
    """AC1: a live match grows the snake and scores when it eats an apple."""
    from game_core import Direction

    engine, publisher = make_engine()
    engine.start_match()
    cells_before = as_cells(engine.snake_cells)

    engine.advance(Direction.RIGHT)

    assert publisher.events_named("apple.eaten"), "advancing right ate no apple"
    assert len(as_cells(engine.snake_cells)) == len(cells_before) + 1
    assert engine.score == 1


def test_the_run_apple_count_is_available_on_the_engine_and_in_the_apple_eaten_payload():
    """AC1: the eaten-apple count is engine state and travels in the event."""
    from game_core import Direction

    engine, publisher = make_engine()
    engine.start_match()

    engine.advance(Direction.RIGHT)

    (eaten,) = publisher.events_named("apple.eaten")
    assert engine.apple_count == 1
    assert eaten.payload["apple_count"] == 1


def test_a_snake_heading_into_a_wall_ends_the_run_with_the_cause_and_final_score():
    """AC2: leaving the board ends the run, naming the wall as the cause."""
    engine, publisher = make_engine()
    engine.start_match()

    result = crash_into_the_wall(engine)

    assert result is not None
    assert "wall" in result.cause.lower()
    assert result.final_score == engine.score == 0


def test_a_snake_hitting_its_own_body_ends_the_run():
    """AC2: a tick onto the snake's own body ends the run as a self hit."""
    from game_core import Direction

    engine, publisher = make_engine()
    engine.start_match()
    engine.advance(Direction.RIGHT)  # eats the start apple and grows
    engine.advance(Direction.RIGHT)  # eats the next apple and grows again
    engine.advance(Direction.UP)  # no apple above the head, so a plain move

    result = engine.advance(Direction.DOWN)

    assert result is not None
    assert "self" in result.cause.lower()


def test_the_ended_run_is_observable_as_a_result_and_a_run_finished_event():
    """AC2: the ended run is shown as a result the engine holds and an event."""
    from game_core import RunResult

    engine, publisher = make_engine()
    engine.start_match()

    result = crash_into_the_wall(engine)

    (finished,) = publisher.events_named("run.finished")
    assert isinstance(result, RunResult)
    assert engine.result.cause == result.cause
    assert finished.payload["cause"] == result.cause
    assert finished.payload["final_score"] == engine.score


def test_advancing_a_finished_run_is_refused_loudly():
    """AC2: ticks after the run ended are refused, never silently ignored."""
    from game_core import Direction

    engine, publisher = make_engine()
    engine.start_match()
    crash_into_the_wall(engine)

    with pytest.raises(ValueError, match="finished"):
        engine.advance(Direction.UP)


def test_turning_straight_backwards_is_refused():
    """AC2: a 180-degree reversal is refused and moves nothing."""
    from game_core import Direction

    engine, publisher = make_engine()
    engine.start_match()
    cells_before = as_cells(engine.snake_cells)

    with pytest.raises(ValueError, match="revers"):
        engine.advance(Direction.LEFT)

    assert as_cells(engine.snake_cells) == cells_before


def test_a_new_match_reads_speed_and_board_size_from_the_knob_store():
    """AC3: a new match pins its speed and board from the knob store."""
    engine, publisher = make_engine(knobs=MatchKnobs(speed=3.0, board_size=12))

    engine.start_match()

    assert engine.speed == 3.0
    assert engine.board_size == 12


def test_each_tick_moves_the_snake_one_cell_within_the_configured_board():
    """AC3: one tick advances the head exactly one cell, body following."""
    from game_core import Direction

    engine, publisher = make_engine(knobs=MatchKnobs(board_size=10))
    engine.start_match()
    cells_before = as_cells(engine.snake_cells)
    head_row, head_column = cells_before[0]

    engine.advance(Direction.UP)

    cells_after = as_cells(engine.snake_cells)
    assert 0 <= cells_after[0][0] < engine.board_size
    assert cells_after[0] == (head_row - 1, head_column)
    assert cells_after[1:] == cells_before[:-1]


def test_the_snake_starts_inside_the_board_heading_right():
    """AC3: a new match puts a live snake on the configured board, facing right."""
    from game_core import Direction

    engine, publisher = make_engine(knobs=MatchKnobs(board_size=10))

    engine.start_match()

    cells = as_cells(engine.snake_cells)
    assert cells, "the match starts with a snake on the board"
    assert engine.heading is Direction.RIGHT
    for row, column in cells:
        assert 0 <= row < engine.board_size
        assert 0 <= column < engine.board_size


def test_a_midgame_knob_update_reaches_the_next_snake_match():
    """AC3: a knob change mid-match only takes hold on the next match."""
    from game_core import Direction

    knobs = MatchKnobs(speed=1.0, board_size=10)
    engine, publisher = make_engine(knobs=knobs)
    engine.start_match()
    assert engine.speed == 1.0
    knobs.update(speed=2.0, board_size=15)
    crash_into_the_wall(engine)

    engine.start_match()

    assert engine.speed == 2.0
    assert engine.board_size == 15
