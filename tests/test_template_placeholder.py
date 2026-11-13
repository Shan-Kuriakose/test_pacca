"""AC2: the scaffold proves itself after it has been copied out of checkout state."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


DEMO_SCRIPT_PATH = Path("examples") / "run_demo.py"
README_PATH = Path("README.md")
DEMO_TIMEOUT_SECONDS = 120
SUITE_TIMEOUT_SECONDS = 120
INNER_TEMPLATE_SUITE = "TEMPLATE_COPY_INNER_SUITE"


def a_template_copy_without_checkout_state(template_root, copy_root):
    ignore_checkout_state = shutil.ignore_patterns(
        ".git",
        "__pycache__",
        ".pytest_cache",
        "*.egg-info",
    )
    shutil.copytree(
        template_root,
        copy_root,
        ignore=ignore_checkout_state,
        dirs_exist_ok=False,
    )
    return copy_root


def test_demo_runs_end_to_end_with_all_three_modules(tmp_path):
    repository_root = Path(__file__).resolve().parents[1]
    readme = (repository_root / README_PATH).read_text(encoding="utf-8")
    demo_script = repository_root / DEMO_SCRIPT_PATH

    assert f"python3 {DEMO_SCRIPT_PATH}" in readme, (
        "the template must document the runnable demo with the repository's "
        "python3 command"
    )

    copied_template = a_template_copy_without_checkout_state(
        repository_root,
        tmp_path / "template-copy",
    )
    assert not (copied_template / ".git").exists(), (
        "the copied scaffold must exclude repository checkout state"
    )

    suite = subprocess.run(
        [sys.executable, str(DEMO_SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=copied_template,
        timeout=DEMO_TIMEOUT_SECONDS,
    )
    assert suite.returncode == 0, (
        "the copied template's demo failed to run end to end:\n"
        f"{suite.stdout}\n{suite.stderr}"
    )

    for module_name in ("game_core", "difficulty_ai", "event_instrumentation"):
        assert module_name in suite.stdout, (
            f"the demo does not prove that {module_name} is wired into the loop"
        )


def test_the_copied_template_test_suite_passes_in_the_copy(tmp_path):
    if os.environ.get(INNER_TEMPLATE_SUITE):
        return "a copied template runs the suite at its own root only"

    repository_root = Path(__file__).resolve().parents[1]
    copied_template = a_template_copy_without_checkout_state(
        repository_root,
        tmp_path / "template-copy",
    )
    assert not (copied_template / ".git").exists(), (
        "the copied scaffold must exclude repository checkout state"
    )

    environment = dict(os.environ)
    environment[INNER_TEMPLATE_SUITE] = "1"
    suite = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        capture_output=True,
        text=True,
        cwd=copied_template,
        env=environment,
        timeout=SUITE_TIMEOUT_SECONDS,
    )
    assert suite.returncode == 0, (
        "a copied scaffold must run its suite without checkout state:\n"
        f"{suite.stdout}\n{suite.stderr}"
    )
