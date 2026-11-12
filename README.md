# Modular AI game template

A reusable starting scaffold for AI projects: three independently scoped
modules under `packages/`, wired together through explicit ports. Copy the
repository, swap the placeholders, and start building.

## The modules

| Module | Source | Role |
| --- | --- | --- |
| game-core | `packages/game-core/src/game_core` | The game loop and the ports it calls out through: `EventPublisher` and `AdaptiveDifficulty`. |
| difficulty-ai | `packages/difficulty-ai/src/difficulty_ai` | `RuleBasedAdaptiveDifficulty`, implementing the `AdaptiveDifficulty` port. This is the adaptive-pattern placeholder. |
| event-instrumentation | `packages/event-instrumentation/src/event_instrumentation` | `InMemoryEventSink`, implementing the `EventPublisher` port. This is the recording placeholder. |

## The dependency rule

`game-core` owns the ports; the other two modules implement them. Neither
adapter imports `game-core` or anything from another module — every module
imports alone, with nothing but its own source on the path. The dependency
between the layers runs from the loop to its adapters, never the reverse.

This is enforced as a test, not by review:
`packages/game-core/tests/test_architecture.py` fails the suite if a
`game-core` source file imports an adapter module, and
`tests/test_module_scope.py` imports each module in a subprocess whose
`PYTHONPATH` holds only its own source.

When code is added at a module boundary, put it on the adapter side of a port
or behind a new port declared in the layer being depended on. Never import
across a module boundary.

## Running the suite

From the repository root, on a clean checkout with no network access:

```sh
python -m pytest
```

With the standard's coverage floor (80%) enforced:

```sh
python -m pytest --cov=packages --cov=examples
```

The test dependencies (`pytest`, `pytest-cov`) are declared in the root
`pyproject.toml` under the `test` extra.

## Running the demo

```sh
python examples/run_demo.py
```

## Copying the template

Minimal placeholder swaps:

1. Replace `packages/difficulty-ai/src/difficulty_ai/adaptive_strategy.py`'s
   `RuleBasedAdaptiveDifficulty` with your own adaptive policy or model. Any
   object answering `next_level(current_level, outcome) -> int` inside a
   bounded range wires straight in — no change to game-core.
2. Replace `packages/event-instrumentation/src/event_instrumentation/in_memory_sink.py`'s
   `InMemoryEventSink` with a persistent sink. Any object answering
   `publish(event)` wires straight in — no change to game-core.
3. Update `examples/demo_app.py`'s `build_components` to wire your adapters
   instead, and rename the projects in the `pyproject.toml` files.

Everything else — the loop, the ports, the tests, the architecture check —
carries over untouched.
