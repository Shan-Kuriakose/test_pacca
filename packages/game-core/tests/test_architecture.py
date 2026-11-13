"""AC3: game-core calls AI and instrumentation only through inward ports."""

import ast
from pathlib import Path


ADAPTER_TOP_LEVEL_NAMES = {"difficulty_ai", "event_instrumentation"}


def adapter_imports_in(source_file):
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    imported_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported_names.append(node.module)

    return [
        imported_name
        for imported_name in imported_names
        if imported_name.split(".")[0] in ADAPTER_TOP_LEVEL_NAMES
    ]


def test_game_core_imports_no_adapter_module():
    module_root = Path(__file__).resolve().parents[2]
    source_root = module_root / "src"
    assert source_root.is_dir(), "game-core module source is missing"

    source_files = sorted(source_root.rglob("*.py"))
    assert source_files, "game-core module has no source files"

    offences = []
    for source_file in source_files:
        for imported_name in adapter_imports_in(source_file):
            offences.append(
                f"{source_file.relative_to(module_root)}: {imported_name}"
            )

    assert not offences, (
        "game-core must not import its adapters:\n" + "\n".join(offences)
    )
    assert (module_root / "pyproject.toml").is_file(), (
        "game-core must carry its own manifest"
    )
