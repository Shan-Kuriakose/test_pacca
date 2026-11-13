"""Shared fixtures for the scaffold's acceptance tests."""

from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parent


@pytest.fixture
def repo_root():
    """Resolve this scaffold's own root, independent of checkout state."""
    return REPOSITORY_ROOT
