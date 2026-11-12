"""GameLoop behaviour with fake ports: publishing, delegation, refusals."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from game_core.difficulty import AdaptiveDifficulty  # noqa: E402
from game_core.events import EventPublisher  # noqa: E402
from game_core.loop import (  # noqa: E402
    DEFAULT_STARTING_LEVEL,
    DIFFICULTY_CHANGED_EVENT,
    ROUND_PLAYED_EVENT,
    GameLoop,
)


class RecordingPublisher(EventPublisher):
    """A fake port implementation that remembers every event it is given."""

    def __init__(self) -> None:
        self.events = []

    def publish(self, event) -> None:
        self.events.append(event)


class StubDifficulty(AdaptiveDifficulty):
    """A fake port implementation that always answers with one level."""

    def __init__(self, level_to_answer_with: int) -> None:
        self._level_to_answer_with = level_to_answer_with

    def next_level(self, current_level: int, outcome: str) -> int:
        return self._level_to_answer_with


def a_loop_with(**overrides):
    """Build a loop with a recording publisher and a stub difficulty."""
    arguments = {
        "publisher": RecordingPublisher(),
        "difficulty": StubDifficulty(4),
        **overrides,
    }
    return GameLoop(**arguments), arguments["publisher"]


def test_a_new_loop_starts_at_the_default_level():
    game_loop, _ = a_loop_with()

    assert game_loop.level == DEFAULT_STARTING_LEVEL


def test_playing_round_delegates_the_level_decision_to_the_port():
    game_loop, _ = a_loop_with()

    assert game_loop.play_round("win") == 4
    assert game_loop.level == 4


def test_playing_round_publishes_round_played_before_difficulty_changed():
    game_loop, publisher = a_loop_with()

    game_loop.play_round("win")

    published_types = [event.event_type for event in publisher.events]
    assert published_types == [ROUND_PLAYED_EVENT, DIFFICULTY_CHANGED_EVENT]


def test_published_events_carry_the_round_knowledge():
    game_loop, publisher = a_loop_with()
    game_loop.play_round("loss")

    round_played, difficulty_changed = publisher.events
    assert round_played.payload == {"outcome": "loss", "level": DEFAULT_STARTING_LEVEL}
    assert difficulty_changed.payload == {"level": 4}


def test_a_missing_publisher_fails_loudly():
    with pytest.raises(ValueError, match="EventPublisher"):
        GameLoop(publisher=None, difficulty=StubDifficulty(2))


def test_a_missing_difficulty_fails_loudly():
    with pytest.raises(ValueError, match="AdaptiveDifficulty"):
        GameLoop(publisher=Mock(), difficulty=None)
