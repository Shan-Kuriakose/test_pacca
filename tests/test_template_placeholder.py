"""AC2: the template runs with minimal placeholder swaps.

The runnable demo wires all three modules -- game-core, difficulty-ai and
event-instrumentation -- and runs from a clean checkout with no network.
"""

import subprocess
import sys

DEMO_SCRIPT_PATH = "examples/run_demo.py"

MODULE_NAMES_REPORTED = (
    "game_core",
    "difficulty_ai",
    "event_instrumentation",
)


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

    missing_names = [
        module_name
        for module_name in MODULE_NAMES_REPORTED
        if module_name not in completed.stdout
    ]
    assert not missing_names, (
        f"the demo does not report wiring {', '.join(missing_names)}"
    )
