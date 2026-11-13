"""AC1: every scaffold module can travel and be tested as its own package."""

import shutil
import subprocess
import sys
from pathlib import Path


MODULE_PACKAGES = ("game-core", "difficulty-ai", "event-instrumentation")
TEST_SUITE_TIMEOUT_SECONDS = 120


def a_module_copy_without_checkout_state(module_root: Path, copy_root: Path):
    ignore_checkout_state = shutil.ignore_patterns(
        ".git",
        "__pycache__",
        ".pytest_cache",
        "*.egg-info",
    )
    shutil.copytree(
        module_root,
        copy_root,
        ignore=ignore_checkout_state,
        dirs_exist_ok=False,
    )
    return copy_root


def run_isolated_import_test(module_root: Path, source_root: Path, tmp_path: Path):
    python_module = module_root.name.replace("-", "_")
    import_root = tmp_path / f"{python_module}-import-only"
    import_root.mkdir()
    environment = {"PYTHONPATH": str(source_root)}
    return subprocess.run(
        [sys.executable, "-c", f"import {python_module}"],
        capture_output=True,
        text=True,
        cwd=import_root,
        env=environment,
        timeout=TEST_SUITE_TIMEOUT_SECONDS,
    )


def run_tests_in_a_clean_module_copy(module_root: Path, copy_root: Path):
    copied_suite = a_module_copy_without_checkout_state(module_root, copy_root)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        capture_output=True,
        text=True,
        cwd=copied_suite,
        timeout=TEST_SUITE_TIMEOUT_SECONDS,
    )


def test_each_module_declares_its_own_manifest_and_imports_alone(tmp_path):
    root = Path(__file__).resolve().parents[1]
    packages_root = root / "packages"
    assert packages_root.is_dir(), "the scaffold must scope its modules under packages/"

    for module_directory in MODULE_PACKAGES:
        module_root = packages_root / module_directory
        manifest = module_root / "pyproject.toml"
        source_root = module_root / "src"
        assert manifest.is_file(), (
            f"{module_directory} has no pyproject.toml of its own to scope it"
        )
        assert source_root.is_dir(), f"{module_directory} has no src/ source directory"

        standalone_import = run_isolated_import_test(module_root, source_root, tmp_path)
        copied_suite = run_tests_in_a_clean_module_copy(
            module_root, tmp_path / f"{module_directory}-copy"
        )
        assert standalone_import.returncode == 0, (
            f"{module_directory} does not import on its own source path:\n"
            f"{standalone_import.stdout}\n{standalone_import.stderr}"
        )
        assert copied_suite.returncode == 0, (
            f"{module_directory} is not an independently scoped package because "
            "its own tests do not run in a checkout-independent copy:\n"
            f"{copied_suite.stdout}\n{copied_suite.stderr}"
        )
