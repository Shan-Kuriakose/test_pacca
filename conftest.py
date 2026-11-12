"""Shared fixtures for the scaffold's acceptance tests."""

from pathlib import Path

import pytest


@pytest.fixture
def repo_root():
    current = Path(__file__).resolve().parent
    while ".git" not in [entry.name for entry in current.iterdir()]:
        current = current.parent
    return current
