"""Shared fixtures for the scaffold's acceptance tests.

A copied template may have dropped its checkout state (.git), so the walk
up from this directory cannot assume it will ever meet .git: it falls
back to this conftest's own directory, which is the repository root.
"""

import pytest
from pathlib import Path


@pytest.fixture
def repo_root():
    conftest_directory = Path(__file__).resolve().parent
    current = conftest_directory
    while ".git" not in [entry.name for entry in current.iterdir()]:
        parent = current.parent
        if parent == current:
            return conftest_directory
        current = parent
    return current
