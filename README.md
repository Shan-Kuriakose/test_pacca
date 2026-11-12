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

- `tests/test_module_scope.py` proves every module declares its own manifest
  and imports with nothing but its own source on the path.
- `packages/game-core/tests/test_architecture.py` fails if game-core source
  ever imports an adapter module.

## Run the demo

```
python examples/run_demo.py
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

## Tests

Run the whole suite from the repository root, with the coverage gate the
project's engineering standard demands:

```
python -m pytest --cov
```

This is the repository's own documented command. It runs pytest with
coverage (pytest-cov, declared in each manifest's `tests` extra), measures
the three modules' source as configured under `[tool.coverage.run]` in the
root `pyproject.toml`, and fails the run when coverage falls below the
standard's 80% floor, which is set as `fail_under` under
`[tool.coverage.report]`. The gate lives in the repository, so nothing has
to agree to it: a run that measures under 80% fails here, not only upstream.

Every module keeps its own tests beside its source (`packages/*/tests/`),
and the root `tests/` hold the module-scope and demo tests.
