"""Shared fixtures for the scaffold's acceptance tests."""

import pytest
from pathlib import Path


def repository_root_found_by_walking_up(start_directory):
    """Walk to the directory holding .git, or the start when none exists."""
    current = start_directory
    while ".git" not in [entry.name for entry in current.iterdir()]:
        if current.parent == current:
            return start_directory
        current = current.parent
    return current


@pytest.fixture
def repo_root():
    return repository_root_found_by_walking_up(Path(__file__).resolve().parent)
