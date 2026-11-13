"""AC3: the knob interface is documented in the README.

The check reads the README's "The knob interface" section, not the whole
file: a name appearing somewhere unrelated must not satisfy it. The
section must name both knob stores, every knob each store holds, the
``update()`` entry point AI tuning goes through, and the match lifecycle
``start_match``/``end_match``/``play_round`` the loop wraps around the
stores.
"""

import re

KNOB_INTERFACE_HEADING = "## The knob interface"

STORE_SECTIONS_DOCUMENTED = (
    "### `game_core.MatchKnobs`",
    "### `difficulty_ai.DifficultyKnobs`",
)

STORE_KNOBS_DOCUMENTED = {
    "### `game_core.MatchKnobs`": (
        "starting_difficulty",
        "speed",
        "board_size",
        "obstacle_count",
    ),
    "### `difficulty_ai.DifficultyKnobs`": (
        "rise_on_success",
        "drop_on_failure",
        "minimum_difficulty",
        "maximum_difficulty",
    ),
}

ENTRY_POINT_DOCUMENTED = "update()"

MATCH_LIFECYCLE_DOCUMENTED = (
    "start_match",
    "play_round",
    "end_match",
)


def the_knob_interface_section(readme_text: str) -> str:
    """The text between the knob-interface heading and the next heading."""
    start = readme_text.find(KNOB_INTERFACE_HEADING)
    assert start != -1, (
        f"the README must carry a {KNOB_INTERFACE_HEADING!r} section"
    )
    next_heading = re.search(
        r"\n## ", readme_text[start + len(KNOB_INTERFACE_HEADING):]
    )
    if next_heading is None:
        return readme_text[start:]
    end = start + len(KNOB_INTERFACE_HEADING) + next_heading.start()
    return readme_text[start:end]


def test_the_readme_documents_the_knob_interface(repo_root):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    section = the_knob_interface_section(readme)

    for store_heading in STORE_SECTIONS_DOCUMENTED:
        assert store_heading in section, (
            f"the knob-interface section must carry a {store_heading!r} "
            "heading naming one of the two knob stores"
        )
        store_text = section.split(store_heading, 1)[1]
        for knob_name in STORE_KNOBS_DOCUMENTED[store_heading]:
            assert f"`{knob_name}`" in store_text, (
                f"{store_heading!r} must document the knob {knob_name!r} "
                "in its knob table"
            )

    assert ENTRY_POINT_DOCUMENTED in section, (
        "the knob-interface section must document the update() entry "
        "point AI tuning goes through"
    )

    for lifecycle_call in MATCH_LIFECYCLE_DOCUMENTED:
        assert f"{lifecycle_call}()" in section, (
            "the knob-interface section must document the match "
            f"lifecycle call {lifecycle_call}()"
        )
