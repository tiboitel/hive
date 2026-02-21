# 🐝 Hive

**Hive** is a tiny, dependency-free Entity-Component-System (ECS) framework for Python.

It gives you a clean simulation core — without magic, decorators, or heavy abstractions.

Perfect for:

- 🎮 Game prototypes
- 🖥 Simulation servers
- 🧪 Experiments
- 🧩 Embedding into larger systems

Small. Explicit. Predictable.

---

# Why Hive?

Hive focuses on doing *just enough*:

- ✅ Deterministic system execution
- ✅ Minimal ECS data model
- ✅ Optional command routing
- ✅ Synchronous event bus
- ✅ Snapshot & restore support
- ✅ Zero runtime dependencies

No async runtime.  
No hidden reflection tricks.  
No metaclass wizardry.  

Just a clean simulation loop you control.

---

# Install

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

Requires **Python 3.9+**

---

# 🚀 60-Second Example

Create a tiny simulation:

```python
from dataclasses import dataclass
from hive import Runtime
from hive.core import System

@dataclass
class Position:
    x: int
    y: int

class Printer(System):
    def update(self, world, dispatcher):
        for eid, pos in world.query(Position):
            print(f"Entity {eid} at ({pos.x}, {pos.y})")

# Create runtime
runtime = Runtime()
world = runtime.world

# Register system
world.register(Printer())

# Create entity
e = world.create_entity()
world.add_component(e, Position(3, 7))

# Run one frame
runtime.step()
```

Output:

```
Entity 0 at (3, 7)
```

That’s it.

---

# 🧠 How Hive Works

Each simulation step:

1. Systems run (can emit commands)
2. Commands are routed to handlers
3. Step counter increments

Architecture overview:

```
Runtime
 ├── World
 │    ├── Store (entities & components)
 │    ├── Systems
 │    ├── EventBus
 │    └── Resources
 └── CommandRouter
```

Everything is explicit and inspectable.

---

# 📦 Core Concepts

## Systems

Systems contain logic:

```python
class Movement(System):
    def update(self, world, dispatcher):
        ...
```

Register them with priority:

```python
world.register(Movement(), priority=10)
```

Lower priority runs earlier.

---

## Components

Plain Python objects (dataclasses recommended):

```python
@dataclass
class Health:
    hp: int
```

Attach to entities:

```python
world.add_component(entity_id, Health(100))
```

Query them:

```python
for eid, health in world.query(Health):
    ...
```

Query a single component for matching entity:

```python 
world.query_single(eid, Health)
    ...
```

---

## Commands (Optional Pattern)

Systems can emit commands:

```python
dispatcher.dispatch(Move(entity, dx=1, dy=0))
```

Register handlers:

```python
runtime.router.register(Move, handle_move)
```

Handlers receive:

```python
def handle_move(cmd, world):
    ...
```

Commands are automatically processed after systems run.

---

## EventBus

Simple synchronous pub/sub:

```python
token = runtime.event_bus.on(MyEvent, handler)
runtime.event_bus.emit(MyEvent(...), runtime.world)
runtime.event_bus.off(token)
```

---

## Resources

Global shared objects stored by type:

```python
runtime.resources.register(Config(seed=42))
cfg = runtime.resources.get(Config)
```

Great for configuration or shared services.

---

## Snapshot / Restore

Serialize world state:

```python
snap = runtime.world.snapshot()
```

Dump:

```python
from hive.serialize import dump_to_json
with open("save.json", "w") as f:
    dump_to_json(snap, f)
```

Load:

```python
from hive.serialize import load_into_world
load_into_world(data, runtime.world)
```

Dataclasses work out of the box.

---

# 📁 Included Examples

- `examples/simple_run.py` — minimal ECS usage
- `examples/move_command.py` — command-driven movement demo

Run:

```bash
python examples/simple_run.py
```

---

# 🎯 Design Goals

Hive is:

- Minimal
- Deterministic
- Embeddable
- Easy to reason about
- Easy to extend

Hive is not:

- A full game engine
- An async framework
- An opinionated architecture

It is a **simulation kernel**.

Build whatever you want on top.

---

# 🤝 Contributing

Keep changes:

- Small
- Clear
- Well-documented
- Backwards-compatible when possible

Hive intentionally stays minimal.

---

# 📜 License

MIT License  
See `LICENSE` file.
