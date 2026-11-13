"""Static module boundaries: no module imports another project module."""

from pathlib import Path
import ast
import sys


import pytest


MODULE_PACKAGES = ("game-core", "difficulty-ai", "event-instrumentation")


def module_root(module_directory: str) -> Path:
    """The source root follows the package directory name."""
    return Path("packages") / module_directory


def imported_names(source_file: Path) -> list[str]:
    """The module names imported at import time."""
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.append(node.module)
    return names


def dynamic_import_names(source_file: Path) -> list[str]:
    """Dynamic import names a source may resolve after import time."""
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    names = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        is_dynamic = (
            isinstance(node.func, ast.Name)
            and node.func.id in ("__import__", "import_module")
            or isinstance(node.func, ast.Attribute)
            and node.func.attr in ("__import__", "import_module")
        )
        if is_dynamic:
            names.append(node.func.id)
    return names


@pytest.mark.parametrize("module_directory", MODULE_PACKAGES)
def test_no_module_imports_another(module_directory: str) -> None:
    python_module = module_directory.replace("-", "_")
    source_root = module_root(module_directory) / "src"
    source_files = sorted(source_root.rglob("*.py"))
    assert source_files, f"{module_directory} has no source files"

    offences = []
    for source_file in source_files:
        relative_name = source_file.relative_to(source_root)
        for imported_name in imported_names(source_file):
            top_level = imported_name.split(".")[0]
            forbidden = (
                top_level not in sys.stdlib_module_names
                and top_level != python_module
            )
            if forbidden:
                offences.append(f"{relative_name} imports {imported_name}")
        offences.extend(
            f"{relative_name} uses {dynamic_name}"
            for dynamic_name in dynamic_import_names(source_file)
        )

    assert not offences, "cross-module imports must not happen:\n" + "\n".join(offences)
