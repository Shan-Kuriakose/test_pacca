# Reusable AI-game project scaffold

A starting template whose code is structured from day one into three
independently scoped modules, so the seam between the game, its adaptive AI
and its instrumentation already exists before any of them grows.

## Modules

| Module | Owns | Depends on |
| --- | --- | --- |
| `packages/game-core` | The game loop, the match lifecycle (`MatchState` with pause, death and restart) and its two ports: `EventPublisher` and `AdaptiveDifficulty`. | Nothing at runtime. |
| `packages/difficulty-ai` | `RuleBasedAdaptiveStrategy`, the default implementation of the difficulty port. | Only its own contracts. It imports nothing from game-core. |
| `packages/event-instrumentation` | `InMemoryEventSink`, the starting implementation of the event port. | Only its own contracts. It imports nothing from game-core. |

## The dependency rule

The engine defines the contracts; the adapters implement them from the
outside, with no import pointing from game-core outward to any adapter. Each
module carries its own `pyproject.toml` and runs on its own source path, so
`packages/difficulty-ai` and `packages/event-instrumentation` can be copied
into another project without carrying the engine along.

The rule is enforced by tests, not by review:

- `tests/test_module_scope.py` proves every module declares its own manifest
  and imports with nothing but its own source on the path.
- `packages/game-core/tests/test_architecture.py` fails if game-core source
  ever imports an adapter module.

## Run the demo

```
python examples/run_demo.py
```

It wires all three modules, plays a few rounds, pauses and resumes
mid-match, then dies and restarts, and prints the difficulty the strategy
reached and the events the sink recorded. No network access and no
credentials are needed.

## The match lifecycle

A match moves through `MatchState.LIVE`, `MatchState.PAUSED` and
`MatchState.DEAD`, and every transition is published as a domain event
(`game.paused`, `game.resumed`, `match.ended`, `match.restarted`):

- `pause()` freezes a live match; play is refused while paused, and
  `resume()` opens play exactly where it froze -- the difficulty trajectory
  does not move while the match is down.
- Losing a round ends the match: `match.ended` is published and play is
  then refused until a restart.
- `restart()` is valid only on a dead match. It asks the difficulty
  strategy's between-games hook, `restarted_match(difficulty_after_death)`,
  for the new match's opening difficulty, adopts that retune, and play
  opens immediately. Which retune is chosen is entirely the strategy's
  answer; the loop only adopts it.

Every refusal -- playing while paused or dead, pausing twice, resuming a
live match, restarting a live match -- raises `ValueError`, following the
template's fail-loudly convention.

## Using this repository as a template

Copy the tree, then swap two things and nothing else:

1. **The adaptive pattern** — replace the rules inside
   `packages/difficulty-ai` with your model. Anything that reads an
   observation with `player_succeeded` and returns the next difficulty,
   and retunes between games through `restarted_match`, satisfies the
   port; no engine change ships with it.
2. **The event sink** — replace `InMemoryEventSink` in
   `packages/event-instrumentation` with your real destination (a message
   bus, a warehouse). A new destination means writing another
   `publish(event)`; the loop is untouched.

The loop itself stays as-is: it only ever calls the two ports.

## Tests

Run the whole suite from the repository root:

```
python -m pytest
```

Every module keeps its own tests beside its source
(`packages/*/tests/`), and the root `tests/` hold the module-scope and
demo suits. Test-only dependencies (`pytest`, `pytest-cov`) are declared in
each manifest's `tests` extra. When run with coverage — as this project's
runner does — the suite is held to the 80% coverage floor from the project's
engineering standard; the floor lives in the runner, not in the repository,
so the gate and the standard cannot drift apart.
