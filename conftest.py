"""Shared fixtures for the scaffold's acceptance tests."""

import pytest
from pathlib import Path


@pytest.fixture
def repo_root():
    # This conftest sits at the repository root, and a template copy may
    # carry no .git at all -- so the root is this file's directory, never
    # whatever a walk up the tree happens to find.
    return Path(__file__).resolve().parent
