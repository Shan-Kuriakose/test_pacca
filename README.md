# Reusable AI-game project scaffold

A starting template whose code is structured from day one into three
independently scoped modules, so the seam between the game, its adaptive AI
and its instrumentation already exists before any of them grows.

## Modules

| Module | Owns | Depends on |
| --- | --- | --- |
| `packages/game-core` | The game loop and its two ports: `EventPublisher` and `AdaptiveDifficulty`. | Nothing at runtime. |
| `packages/difficulty-ai` | `RuleBasedAdaptiveStrategy`, the default implementation of the difficulty port. | Only its own contracts. It imports nothing from game-core. |
| `packages/event-instrumentation` | `InMemoryEventSink`, the starting implementation of the event port. | Only its own contracts. It imports nothing from game-core. |

## The dependency rule

The engine defines the contracts; the adapters implement them from the
outside, with no import pointing from game-core outward to any adapter. Each
module carries its own `pyproject.toml` and runs on its own source path, so
`packages/difficulty-ai` and `packages/event-instrumentation` can be copied
into another project without carrying the engine along.

The rule is enforced by tests, not by review:

- `tests/test_contract_pins.py` proves every module declares its own manifest,
  imports with nothing but its own source on the path, and keeps adapter
  contract pins byte-for-byte identical to the game-core source.
- `packages/game-core/tests/test_architecture.py` fails if game-core source
  ever imports an adapter module, while the root module-scope boundary test
  fails if an adapter imports back into the loop.

## Run the demo

```
python3 examples/run_demo.py
```

It wires all three modules, plays a few rounds, and prints the difficulty the
strategy reached and the events the sink recorded. No network access and no
credentials are needed.

## Using this repository as a template

Copy the tree, then swap two things and nothing else:

1. **The adaptive pattern** — replace the rules inside
   `packages/difficulty-ai` with your model. Anything that reads an
   observation with `player_succeeded` and returns the next difficulty
   satisfies the port; no engine change ships with it.
2. **The event sink** — replace `InMemoryEventSink` in
   `packages/event-instrumentation` with your real destination (a message
   bus, a warehouse). A new destination means writing another
   `publish(event)`; the loop is untouched.

The loop itself stays as-is: it only ever calls the two ports.

## The knob interface

Every tunable parameter lives in one of two centralized, validating knob
stores. Nothing in the loop or the strategy reads a hard-coded value: each
match start and each round reads the store, so the AI layer can change
difficulty parameters mid-game and between games without touching code.

The loop keeps an explicit match lifecycle around the stores:
`start_match()` reads every knob and refuses while a match is still in
progress, `play_round()` refuses before a match has started, and
`end_match()` closes the match so a new one can read the store fresh.

### `game_core.MatchKnobs`

The game's own knobs, held by the loop and read on every `start_match()`
call and every round:

| Knob | Default | Meaning |
| --- | --- | --- |
| `starting_difficulty` | `0.5` | The difficulty every match begins at. |
| `speed` | `1.0` | How fast the game runs. |
| `board_size` | `10` | The playfield's size. |
| `obstacle_count` | `5` | How many obstacles a match places. |

Tune it by calling `update()` — mid-game, where a change reaches the next
round, or between games, where `end_match()` closes the running match and
`start_match()` reads it fresh:

```python
knobs = MatchKnobs()          # all defaults
loop.start_match()            # the match reads every knob from the store
knobs.update(speed=2.5)       # mid-game: the next round runs at the new speed
loop.end_match()              # close the match
knobs.update(board_size=16)
loop.start_match()            # between games: the new match reads it
```

### `difficulty_ai.DifficultyKnobs`

The strategy's knobs, read on every `adjust()` call. (The original template
name `DifficultyStepSettings` still names the same store.)

| Knob | Default | Meaning |
| --- | --- | --- |
| `rise_on_success` | `0.1` | How far a won round raises difficulty. |
| `drop_on_failure` | `0.15` | How far a lost round lowers difficulty. |
| `minimum_difficulty` | `0.1` | The floor difficulty clamps to. |
| `maximum_difficulty` | `1.0` | The ceiling difficulty clamps to. |

Tune it the same way, mid-run without rewiring:

```python
knobs = DifficultyKnobs()
knobs.update(drop_on_failure=0.05)
```

Both stores validate every change: `update()` refuses an unknown parameter
name and any invalid value with a loud `ValueError` naming the knob, and it
validates the whole configuration before a single field moves. The loop
refuses just as loudly: `play_round()` before any `start_match()`, a second
`start_match()` while a match runs, and `end_match()` with no match running
all raise `ValueError` stating what is wrong.

## Tests

Run the whole suite from the repository root:

```
python3 -m pytest
```

Every module keeps its own tests beside its source
(`packages/*/tests/`), and the root `tests/` hold the module-scope and
demo suits. Test-only dependencies (`pytest`, `pytest-cov`) are declared in
each manifest's `tests` extra. When run with coverage — as this project's
runner does — the suite is held to the 80% coverage floor from the project's
engineering standard; the floor lives in the runner, not in the repository,
so the gate and the standard cannot drift apart.
