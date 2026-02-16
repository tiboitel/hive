# Hive

Hive is a minimal, dependency-light Entity-Component-System (ECS) micro-framework
designed for small servers and game prototypes. It focuses on clarity, minimalism, and
easy embedding into larger projects.

## Installation

Install from source or using your preferred packaging workflow. This project uses
standard Python packaging metadata in `pyproject.toml` and targets modern build
backends.

```bash
pip install .
```

## Package contents

- `src/core.py` — World, System base class, CommandQueue, and query APIs
- `src/store.py` — backward-compatible wrapper around `World`
- `src/runtime.py` — runtime orchestration and convenience aliases
- `src/events.py` — synchronous EventBus
- `src/resources.py` — ResourceRegistry
- `src/serialize.py` — snapshot/load helpers (dataclass-friendly)

## Examples

- `examples/simple_run.py` — minimal host example
- `examples/move_command.py` — command-driven demo

## Quick usage

EventBus

```py
# subscribe
token = runtime.event_bus.on(MyEvent, handler)
# emit
runtime.event_bus.emit(MyEvent(...), runtime.world, runtime._dispatcher)
```

Resources

```py
runtime.resources.register('config', {'seed': 42})
cfg = runtime.resources.get('config')
```

Snapshot / Load

```py
snap = runtime.world.snapshot()
from src.serialize import dump_to_json, load_into_world
with open('snap.json','w') as f:
    dump_to_json(snap, f)

# later
import json
with open('snap.json') as f:
    data = json.load(f)
load_into_world(data, runtime.world)
```

## Development

- Run tests: `pytest`
- Lint/format: use your preferred tools; keep changes minimal to preserve the small
  codebase and style.

## Contributing

Keep changes focused, small, and well-documented.

## License

See the `LICENSE` file in the repository root.
