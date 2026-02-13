# tiny_ecs

A minimal, generic ECS (Entity-Component-System) micro-framework. The project
provides a small core suitable for building domain-specific simulations or
games while keeping framework code free of domain logic.

## Key components
- `src/core.py` — World, System base class, and CommandQueue
- `src/store.py` — backward-compatible wrapper around `World` (entity/component API)
- `src/runtime.py` — Runtime container that holds the World, Store and Dispatcher
- `src/command` — simple command dataclasses and dispatcher

## Getting started

1. Install in editable mode (recommended):

```
pip install -e .
```

2. Run the example host under `examples/simple_run.py`:

```
python examples/simple_run.py
```

## Project goals
- Keep the core small, domain-agnostic and easy to reason about
- Provide a clean command dispatching mechanism for action routing
- Remain friendly to small servers and single-maintainer workflows

## Next steps
- Add an EventBus for decoupled communication between systems
- Add serialization / snapshotting for persistence
- Provide more example host apps (e.g. tile-based game) under `examples/`
