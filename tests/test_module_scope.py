"""AC1: game-core, difficulty-AI and event-instrumentation are independently scoped modules.

Each module lives in its own directory under packages/, declares its own
manifest, and imports with nothing but its own source on the path.
"""

import os
import subprocess
import sys

MODULE_IMPORT_NAMES = {
    "game-core": "game_core",
    "difficulty-ai": "difficulty_ai",
    "event-instrumentation": "event_instrumentation",
}


def _probe_imports_alone(repo_root, subdirectory, import_name, sibling_imports):
    """Import one module in a subprocess whose path holds only its own source."""
    source_root = repo_root / "packages" / subdirectory / "src"
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(source_root)
    probe = f"import sys\nimport {import_name}\n"
    probe += f"assert not any(name in sys.modules for name in {sorted(sibling_imports)!r})\n"
    completed = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        cwd=repo_root,
        env=environment,
        timeout=60,
    )
    assert completed.returncode == 0, (
        f"{subdirectory} does not import on its own:\n{completed.stderr}"
    )
    return completed


def test_each_module_declares_its_own_manifest_and_imports_alone(repo_root):
    packages_root = repo_root / "packages"
    assert packages_root.is_dir(), "the template must scope its modules under packages/"

    for subdirectory, import_name in MODULE_IMPORT_NAMES.items():
        module_root = packages_root / subdirectory
        assert module_root.is_dir(), f"module {subdirectory} is missing under packages/"

        manifest = module_root / "pyproject.toml"
        assert manifest.is_file(), (
            f"{subdirectory} has no pyproject.toml of its own to scope it"
        )

        sibling_imports = {
            name for name in MODULE_IMPORT_NAMES.values() if name != import_name
        }
        _probe_imports_alone(
            repo_root, subdirectory, import_name, sibling_imports
        )
