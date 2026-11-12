"""ITS-2 / AC2: the copied template runs its demo without the original checkout.

The scaffolding must travel with the copied tree, not with the checkout it
was copied from: ``python examples/run_demo.py`` wires the three modules,
plays its match and exits cleanly from a copy that kept no .git, using only
the copy's own files.
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

DEMO_TIMEOUT_SECONDS = 60

# The copied-template suite test sets this variable for any pytest run it
# starts inside a copy, so this test must check the same literal to stand
# down there.
INSIDE_TEMPLATE_COPY_GATE = "TEMPLATE_COPY_INNER_SUITE"


def a_clean_copy_without_checkout_state(template_root, copy_root):
    """Copy the template, leaving its checkout state behind in the original."""
    state_to_leave_behind = shutil.ignore_patterns(*CHECKOUT_STATE_AND_CACHES)
    shutil.copytree(template_root, copy_root, ignore=state_to_leave_behind)
    return copy_root


def the_demo_run_in(copied_template):
    """Run the copied template's demo with no network and no credentials."""
    return subprocess.run(
        [sys.executable, str(copied_template / DEMO_SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=copied_template,
        timeout=DEMO_TIMEOUT_SECONDS,
    )


def test_a_copied_template_runs_the_demo_without_the_original_checkout(
    repo_root, tmp_path
):
    """AC2: the demo runs in a copy that dropped all checkout state."""
    if os.environ.get(INSIDE_TEMPLATE_COPY_GATE):
        pytest.skip("a copied template runs the demo at its own root only")

    copied_template = a_clean_copy_without_checkout_state(
        repo_root, tmp_path / "template-copy"
    )
    completed = the_demo_run_in(copied_template)

    assert completed.returncode == 0, (
        f"the demo failed inside a copied template:\n{completed.stderr}"
    )
    for module_name in MODULE_NAMES_REPORTED:
        assert module_name in completed.stdout, (
            f"the copied template's demo does not report wiring {module_name}"
        )
