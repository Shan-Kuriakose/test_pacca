"""AC2: the knob interface is documented in the README.

The documentation must name both knob stores, every knob each holds, and
the entry points AI tuning and the match lifecycle go through.
"""

KNOB_NAMES_DOCUMENTED = (
    "MatchKnobs",
    "DifficultyKnobs",
    "starting_difficulty",
    "speed",
    "board_size",
    "obstacle_count",
    "rise_on_success",
    "drop_on_failure",
    "minimum_difficulty",
    "maximum_difficulty",
    "update",
    "start_match",
)


def test_the_readme_documents_the_knob_interface(repo_root):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")

    for knob_name in KNOB_NAMES_DOCUMENTED:
        assert knob_name in readme, (
            f"the README must document the knob {knob_name!r}"
        )
