"""AC1: every scaffold module can travel and be tested as its own package."""

import shutil
import subprocess
import sys
from pathlib import Path


MODULE_PACKAGES = ("game-core", "difficulty-ai", "event-instrumentation")
TEST_SUITE_TIMEOUT_SECONDS = 120


def a_module_copy_without_checkout_state(module_root, copy_root):
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


def test_each_module_declares_its_own_manifest_and_imports_alone(tmp_path):
    packages_root = Path(__file__).resolve().parents[1] / "packages"
    assert packages_root.is_dir(), "the scaffold must scope its modules under packages/"

    for module_name in MODULE_PACKAGES:
        module_root = packages_root / module_name
        manifest = module_root / "pyproject.toml"
        source_root = module_root / "src"

        assert manifest.is_file(), (
            f"{module_name} has no pyproject.toml of its own to scope it"
        )
        assert source_root.is_dir(), f"{module_name} has no src/ source directory"

        copied_suite = a_module_copy_without_checkout_state(
            module_root,
            tmp_path / f"{module_name}-copy",
        )
        suite = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            capture_output=True,
            text=True,
            cwd=copied_suite,
            timeout=TEST_SUITE_TIMEOUT_SECONDS,
        )
        assert suite.returncode == 0, (
            f"{module_name} is not an independently scoped package because "
            "its own tests do not run in a checkout-independent copy:\n"
            f"{suite.stdout}\n{suite.stderr}"
        )
