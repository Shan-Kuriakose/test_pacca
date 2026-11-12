"""AC2 support: the demo orchestration is real, tested code.

examples/run_demo.py is the runner; demo_app.py is the wiring itself. Both
are executed here in-process so the orchestration stays under test.
"""

import importlib.util
from pathlib import Path

DEMO_SCRIPT = Path(__file__).resolve().parent.parent / "examples" / "run_demo.py"
WIRED_MODULE_NAMES = ("game_core", "difficulty_ai", "event_instrumentation")


def _executed_demo_script():
    spec = importlib.util.spec_from_file_location("run_demo", DEMO_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_demo_wires_all_three_modules_and_reports_them(capsys):
    run_demo = _executed_demo_script()
    output = capsys.readouterr().out

    for module_name in WIRED_MODULE_NAMES:
        assert module_name in output, f"the demo does not report wiring {module_name}"


def test_the_demo_publishes_two_events_per_round(capsys):
    run_demo = _executed_demo_script()
    events_published = run_demo.main()

    assert events_published == 12
