# Reusable AI Game Template

A starting template for future AI projects: a game loop, an adaptive
difficulty layer and event instrumentation, packaged as three independently
scoped modules. Copy the repository, swap the placeholders the README names,
and the scaffold runs.

## The modules

| Module | Directory | Responsibility |
| --- | --- | --- |
| game-core | `packages/game-core` | The round loop and the two ports it depends on: `EventPublisher` and `AdaptiveDifficulty`. No runtime dependencies. |
| difficulty-ai | `packages/difficulty-ai` | The adaptive difficulty policy. Implements the `AdaptiveDifficulty` port's shape without importing game-core. |
| event-instrumentation | `packages/event-instrumentation` | An in-memory event sink. Implements the `EventPublisher` port's shape without importing game-core. |

### The dependency rule

The ports live in game-core; the adapters implement them from the outside,
following the shapes of the contracts rather than importing them. Nothing in
`difficulty-ai` or `event-instrumentation` imports `game_core`, and an
architecture test (`packages/game-core/tests/test_architecture.py`) fails CI
if that ever changes. When a module boundary needs a shared value type, add a
versioned contracts package deliberately — never a shared import.

A module's scope is itself under test (`tests/test_module_scope.py`): every
directory under `packages/` declares its own `pyproject.toml` and imports on
its own source only.

## Running the tests

From the repository root, on a clean checkout, with no network access and no
credentials:

```sh
pip install -e '.[test]'
pytest
```

## Copying the template (the placeholder swaps)

1. Copy `packages/game-core` unchanged: the loop and the ports are the
   reusable part.
2. Copy `packages/difficulty-ai` and replace
   `RuleBasedAdaptiveDifficulty` with the project's own model-backed policy;
   the only contract is `next_difficulty(current_difficulty, outcome) -> int`.
   Keep the class rule-free if the model decides everything.
3. Copy `packages/event-instrumentation` and replace `InMemoryEventSink`
   when real storage is wanted; the only contract is
   `publish(event) -> None`, and a write that never landed must raise.
4. Update `examples/run_demo.py` to wire the project's replacements. It runs
   end to end from a clean checkout as the template's executable proof
   (`tests/test_template_placeholder.py` keeps it that way).

```sh
python examples/run_demo.py
```
