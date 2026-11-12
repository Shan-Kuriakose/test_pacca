"""AC3: the AI layer is not entangled with game loop internals.

game-core owns the ports; the adapters (difficulty-ai, event-instrumentation)
implement them. The dependency rule is checked here as a test, not by review:
the game-core source must never import an adapter module.
"""

import ast

ADAPTER_TOP_LEVEL_NAMES = {"difficulty_ai", "event_instrumentation"}


def _adapter_imports_in(source_file):
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imports.append(node.module)
    return [
        name
        for name in imports
        if name.split(".")[0] in ADAPTER_TOP_LEVEL_NAMES
    ]


def test_game_core_imports_no_adapter_module(repo_root):
    game_core_source = repo_root / "packages" / "game-core" / "src"
    assert game_core_source.is_dir(), "game-core module source is missing"
    source_files = sorted(game_core_source.rglob("*.py"))
    assert source_files, "game-core module has no source files"

    offences = []
    for source_file in source_files:
        for imported in _adapter_imports_in(source_file):
            offences.append(f"{source_file.relative_to(repo_root)}: {imported}")

    assert not offences, (
        f"game-core must not import its adapters:\n" + "\n".join(offences)
    )
