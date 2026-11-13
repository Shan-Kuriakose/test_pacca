"""Versioned contract pins and module runtime isolation under AC1."""

from pathlib import Path
import subprocess
import sys
import pytest


MODULE_PACKAGES = ("game-core", "difficulty-ai", "event-instrumentation")
PinnedContracts: tuple[tuple[str, str, str], ...] = (
    (
        "difficulty_ai",
        "game_core.contracts.adaptive_difficulty.v1",
        "difficulty_ai.contracts.adaptive_difficulty.v1",
    ),
    (
        "event_instrumentation",
        "game_core.contracts.event_publisher.v1",
        "event_instrumentation.contracts.event_publisher.v1",
    ),
)


def contract_path(module_name: str) -> Path:
    """Map a Python module name to the package directory that owns it."""
    top_level = module_name.split(".")[0]
    package_directory = {
        "game_core": "game-core",
        "difficulty_ai": "difficulty-ai",
        "event_instrumentation": "event-instrumentation",
    }[top_level]
    return (
        Path("packages")
        / package_directory
        / "src"
        / Path(*module_name.split(".")).with_suffix(".py")
    )


@pytest.mark.parametrize(("adapter_module", "source_module", "pinned_module"), PinnedContracts)
def test_the_adapter_pins_the_published_contract_version(
    adapter_module: str, source_module: str, pinned_module: str
) -> None:
    source = contract_path(source_module).read_bytes()
    pin = contract_path(pinned_module).read_bytes()

    assert source == pin, f"{adapter_module} must pin the exact published contract"


def test_each_module_imports_alone_in_a_clean_subprocess(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[1]
    for module_directory in MODULE_PACKAGES:
        python_module = module_directory.replace("-", "_")
        source_root = (
            repository_root
            / "packages"
            / module_directory
            / "src"
        )
        isolated_cwd = tmp_path / f"{module_directory}-import"
        isolated_cwd.mkdir()

        result = subprocess.run(
            [sys.executable, "-c", f"import {python_module}"],
            capture_output=True,
            text=True,
            cwd=isolated_cwd,
            env={"PYTHONPATH": str(source_root)},
            timeout=10,
        )

        assert result.returncode == 0, (
            f"{module_directory} does not import on its own source path:\n"
            f"{result.stdout}\n{result.stderr}"
        )
