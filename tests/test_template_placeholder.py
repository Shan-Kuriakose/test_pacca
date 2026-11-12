"""AC2: the template runs with minimal placeholder swaps.

The runnable demo wires all three modules -- game-core, difficulty-ai and
event-instrumentation -- and runs from a clean checkout with no network.
The scaffolding travels with a copy of the template, not with the original
checkout: a copied template that kept no checkout state (.git) runs its
whole test suite too.
"""

import os
import shutil
import subprocess
import sys

import pytest

DEMO_SCRIPT_PATH = "examples/run_demo.py"

MODULE_NAMES_REPORTED = (
    "game_core",
    "difficulty_ai",
    "event_instrumentation",
)

CHECKOUT_STATE_AND_CACHES = (
    ".git",
    "__pycache__",
    ".pytest_cache",
    "*.egg-info",
)

TEST_SUITE_TIMEOUT_SECONDS = 120

_RUNNING_INSIDE_A_TEMPLATE_COPY = "TEMPLATE_COPY_INNER_SUITE"


def test_demo_runs_end_to_end_with_all_three_modules(repo_root):
    demo_script = repo_root / DEMO_SCRIPT_PATH
    assert demo_script.is_file(), (
        "examples/run_demo.py is missing; the template needs a runnable proof"
    )

    completed = subprocess.run(
        [sys.executable, str(demo_script)],
        capture_output=True,
        text=True,
        cwd=repo_root,
        timeout=120,
    )
    assert completed.returncode == 0, (
        f"the demo failed to run end to end:\n{completed.stderr}"
    )

    for module_name in MODULE_NAMES_REPORTED:
        assert module_name in completed.stdout, (
            f"the demo does not report wiring {module_name}"
        )


def a_clean_copy_without_checkout_state(template_root, copy_root):
    """Copy the template, leaving its checkout state behind in the original."""
    state_to_leave_behind = shutil.ignore_patterns(*CHECKOUT_STATE_AND_CACHES)
    shutil.copytree(template_root, copy_root, ignore=state_to_leave_behind)
    return copy_root


def the_test_suite_run_in(copied_template):
    """Run the copied template's whole suite with the same interpreter."""
    environment = dict(os.environ)
    environment[_RUNNING_INSIDE_A_TEMPLATE_COPY] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        capture_output=True,
        text=True,
        cwd=copied_template,
        env=environment,
        timeout=TEST_SUITE_TIMEOUT_SECONDS,
    )


def test_the_copied_template_test_suite_passes_in_the_copy(repo_root, tmp_path):
    """AC2: the scaffolding runs in a copy that dropped all checkout state."""
    if os.environ.get(_RUNNING_INSIDE_A_TEMPLATE_COPY):
        pytest.skip("a copied template runs the suite at its own root only")

    copied_template = a_clean_copy_without_checkout_state(
        repo_root, tmp_path / "template-copy"
    )
    completed = the_test_suite_run_in(copied_template)

    assert completed.returncode == 0, (
        "the suite must pass inside a copied template with no .git "
        f"anywhere in its tree:\n{completed.stdout}\n{completed.stderr}"
    )
