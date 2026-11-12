"""Runs the browser-client's TypeScript domain code through Node on behalf of pytest.

The repository's runnable suite is pytest, but this story's production code is
TypeScript. Each test hands a small driver script to Node, which imports the
production sources directly and reports what it observed as JSON. The tests
then assert on behaviour, never on file structure.
"""

import json
import subprocess
import tempfile
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = PACKAGE_ROOT / "src" / "domain"
ADAPTERS_ROOT = PACKAGE_ROOT / "src" / "adapters"


def run_driver(source: str) -> dict:
    driver = tempfile.NamedTemporaryFile(
        "w", suffix=".mts", delete=False, prefix="browser_client_driver_"
    )
    driver.write(
        source.replace("DOMAIN_ROOT_PLACEHOLDER", str(DOMAIN_ROOT)).replace(
            "ADAPTERS_ROOT_PLACEHOLDER", str(ADAPTERS_ROOT)
        )
    )
    driver.close()
    completed = subprocess.run(
        ["node", "--experimental-strip-types", driver.name],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "Node driver failed while exercising the browser-client sources "
            "(missing modules and missing behaviour both surface this way):\n"
            f"{completed.stderr}"
        )
    return _decode_report(completed.stdout)


def _decode_report(stdout: str) -> dict:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        for line in reversed(stdout.splitlines()):
            stripped = line.strip()
            if stripped.startswith("{"):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    continue
        raise AssertionError(
            f"Node driver printed no JSON report. stdout was:\n{stdout}"
        )
