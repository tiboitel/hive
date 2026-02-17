# Hive Architecture

Overview of the Hive ECS micro-framework architecture, design decisions, and component interactions.

## Table of Contents

- [Design Philosophy](#design-philosophy)
- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Design Decisions](#design-decisions)
- [Extensibility](#extensibility)

---

## Design Philosophy

Hive is built on five core principles:

1. **Minimalism**: Only essential ECS features; no bloat
2. **Genericity**: Zero domain logic; framework-agnostic
3. **Simplicity**: Easy to understand, use, and extend
4. **Robustness**: Handles edge cases gracefully
5. **Efficiency**: Reasonable performance without premature optimization

The framework prioritizes developer experience for single-maintainer projects while remaining suitable for small-to-medium scale simulations (1000+ entities).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Runtime                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Run Systems    2. Route Commands   3. Cleanup   │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                              │
│         ┌────────────────────┼────────────────────┐        │
│         ▼                    ▼                    ▼        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    World     │◄───│  Dispatcher  │    │   Router     │  │
│  │              │    │              │    │              │  │
│  │  ┌────────┐  │    │  Queue cmds  │    │  Map cmds    │  │
│  │  │ Store  │  │    │  from sys    │    │  to handlers │  │
│  │  │        │  │    └──────────────┘    └──────────────┘  │
│  │  │Entities│  │            ▲                    ▲        │
│  │  │Comps   │  │            │                    │        │
│  │  └────────┘  │    ┌───────┴──────┐             │        │
│  │              │    │   Systems    │─────────────┘        │
│  │  ┌────────┐  │    │   (user)     │                      │
│  │  │Events  │  │    └──────────────┘                      │
│  │  └────────┘  │                                          │
│  │  ┌────────┐  │                                          │
│  │  │Resources│  │                                          │
│  │  └────────┘  │                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Runtime

The **Runtime** orchestrates the simulation loop. It is the main entry point for host applications.

**Responsibilities:**
- Coordinate World, Dispatcher, and Router
- Execute simulation steps in correct order
- Provide convenient access to subsystems

**Key Insight:** Runtime separates the "how" (orchestration) from the "what" (simulation logic). The World contains the simulation; Runtime runs it.

### 2. World

The **World** is the simulation container. It owns all simulation state and systems.

**Composition:**
- `Store`: Entity and component data
- `EventBus`: Decoupled communication
- `ResourceRegistry`: Static/shared data
- `List[System]`: Registered systems with priorities

**Design Pattern:** World acts as a Façade, providing convenient methods that delegate to Store. This allows Store to be swapped/optimized without changing World API.

### 3. Store

The **Store** is the data layer. It owns entities, components, and queries.

**Storage Strategy:** Dictionary-based component storage
```python
_components: Dict[Type, Dict[int, Component]]
# {Position: {0: Position(1,2), 1: Position(3,4)}, ...}
```

**Entity Recycling:**
- Destroyed entity IDs are added to `_free_ids` list
- New entities reuse IDs from free list (FIFO)
- Safety limit (10,000) prevents memory bloat

**Query Implementation:**
- Set intersection for multi-component queries
- Deterministic output (sorted entity IDs)
- Empty result if any component type missing (ECS semantics)

### 4. Systems

**Systems** implement game logic by processing entities with specific components.

**Contract:**
- Inherit from `System` base class
- Implement `update(world, dispatcher)` method
- Access data via World/Store API
- Emit commands via Dispatcher
- Emit events via World.event_bus

**Execution Order:**
Systems run by priority (lower = earlier). Same-priority order is registration order.

### 5. EventBus

**EventBus** provides decoupled pub/sub communication.

**Characteristics:**
- Synchronous (handlers run immediately on emit)
- Type-based subscription
- Exception isolation (one handler failure doesn't break others)
- Token-based unsubscription

**Use Cases:**
- Cross-system communication without direct coupling
- Reaction triggers ("when X happens, do Y")
- Debugging/logging hooks

### 6. ResourceRegistry

**ResourceRegistry** stores global/shared objects accessed by systems.

**Storage:** Type-based dictionary
```pythonn
```

**Use Cases:**
- Configuration objects
- Random number generators
- Asset references
- Shared caches

### 7. CommandDispatcher & Router

**CommandDispatcher:** Generic command queue
- Systems emit commands (intents/actions)
- Queue decouples emission from processing
- Host pulls commands for processing

**CommandRouter:** Type-safe handler registry
- Maps command types to handler functions
- Eliminates isinstance() chains
- Enables modular command handling

**Separation of Concerns:**
- Dispatcher: "Collect commands"
- Router: "Route commands to handlers"
- Runtime coordinates both

---

## Data Flow

### Normal Simulation Step

```
1. Runtime.step() called

2. World.step(dispatcher)
   └─ For each system (priority order):
      └─ system.update(world, dispatcher)
         └─ Systems query entities, modify components
         └─ Systems emit commands via dispatcher
         └─ Systems emit events via world.event_bus

3. commands = dispatcher.pop_all()

4. router.handle_all(commands, world)
   └─ For each command:
      └─ route to registered handler
         └─ Handler modifies world state

5. steps += 1
```

### Event Flow

```
System/Event Source
       │
       ▼
world.event_bus.emit(EventType(...), world, dispatcher)
       │
       ▼
EventBus.emit()
       │
       ├──► Handler 1(event, world, dispatcher)
       ├──► Handler 2(event, world, dispatcher)
       └──► Handler N(event, world, dispatcher)
```

### Component Query Flow

```
System calls world.query(Position, Velocity)
       │
       ▼
Store.query(Position, Velocity)
       │
       ├──► Get entity sets for each component type
       │         {0, 1, 2} for Position
       │         {1, 2, 3} for Velocity
       │
       ├──► Compute intersection: {1, 2}
       │
       └──► Yield (entity, comp1, comp2) tuples
                (1, Position(1,2), Velocity(1,0))
                (2, Position(3,4), Velocity(0,1))
```

---

## Design Decisions

### 1. Dictionary-Based Storage (vs Archetypes)

**Decision:** Use dictionary mapping `Type → Dict[Entity, Component]`

**Rationale:**
- Simple to understand and debug
- Good enough for <1000 entities
- Easy to serialize
- Allows sparse component sets efficiently

**Trade-off:** Cache locality worse than archetype storage. Optimization (archetypes) deferred to P3.

### 2. Entity as Integer IDs

**Decision:** Entities are simple integers, not objects

**Rationale:**
- Lightweight (just an int)
- Easy to serialize
- No entity object lifecycle complexity
- Clear ownership (Store owns data)

### 3. Component = Any Object

**Decision:** Components can be any Python object

**Rationale:**
- No artificial constraints
- Dataclasses work out of the box
- Classes, namedtuples, simple objects all valid

**Best Practice:** Use `@dataclass` for automatic serialization support.

### 4. System as Class with update() Method

**Decision:** Systems are classes with a single update method

**Rationale:**
- Allows systems to maintain internal state
- Familiar OOP pattern
- Easy to test (instantiate and call update)

**Alternative Considered:** Function-based systems. Rejected: limits stateful systems.

### 5. Synchronous Event Bus

**Decision:** Events are handled synchronously

**Rationale:**
- Simpler mental model
- Predictable execution order
- No race conditions
- Easier debugging

**Trade-off:** Long-running handlers block the simulation step.

### 6. No Built-in Cleanup System

**Decision:** Framework provides `Destroyed` marker component but no automatic cleanup

**Rationale:**
- Cleanup policy is domain-specific
- User might want batch cleanup, pooling, etc.
- Keeps framework minimal

**Pattern:** Users register a cleanup system:
```python
class CleanupSystem(System):
    def update(self, world, dispatcher):
        for eid in world.query_entities(Destroyed):
            world.destroy_entity(eid)
```

### 7. Explicit Priority (not Dependencies)

**Decision:** Systems specify priority (int), not dependencies

**Rationale:**
- Simpler than dependency graph
- Easier to reason about
- Sufficient for most use cases

**Trade-off:** Manual priority management in large projects.

### 8. Command Pattern for Actions

**Decision:** Use command objects for cross-system actions

**Rationale:**
- Decouples intent from execution
- Enables command queuing, batching, logging
- Natural fit for networked games

---

## Extensibility

### Adding Custom Storage

Store can be subclassed or replaced:

```python
class ArchetypeStore(Store):
    # Implement archetype-based storage
    pass

world._store = ArchetypeStore()
```

### Custom Component Types

Any object works. For serialization, register custom serializers:

```python
from hive.serialize import register_serializer

class MyComponent:
    def __init__(self, value):
        self.value = value

register_serializer(
    MyComponent,
    to_dict=lambda c: {"value": c.value},
    from_dict=lambda d: MyComponent(d["value"])
)
```

### Custom Events

Events are plain objects. Use dataclasses:

```python
@dataclass
class CustomEvent:
    entity_id: int
    data: dict
```

### System Groups/Phases

While Hive doesn't have built-in phases, you can implement them:

```python
world.register(InputSystem(), priority=-200)
world.register(PhysicsSystem(), priority=-100)
world.register(AISystem(), priority=0)
world.register(RenderSystem(), priority=100)
```

### Plugins

The framework is designed for composition, not inheritance. "Plugins" are just modules that set up systems and handlers:

```python
# physics_plugin.py
def install(runtime):
    runtime.world.register(PhysicsSystem())
    runtime.world.register(CollisionSystem())
    runtime.router.register(MoveCommand, handle_move)
```

---

## Performance Considerations

### Current Implementation

- **Entity creation:** O(1) amortized (with recycling)
- **Component add/remove:** O(1)
- **Single component query:** O(1) (dict lookup)
- **Multi-component query:** O(min_set_size) for intersection
- **System iteration:** O(entities_with_components)

### Scalability

| Metric | Approximate Limit |
|--------|-------------------|
| Entities | 10,000+ (memory bound) |
| Component types | 100s (dict overhead) |
| Systems | 100s (execution time) |
| Events/step | 1000s (handler time) |

### Optimization Path

If performance becomes an issue:

1. **P3: Archetype Storage** - Cache-friendly storage for high entity counts
2. **Spatial indexing** - Add spatial hash/grid as resource
3. **Command batching** - Process commands in batches
4. **Event filtering** - Only emit events when subscribers exist

---

## Security & Safety

- No sandboxing (Python)
- Handlers should validate inputs
- Event handlers are isolated (exceptions don't propagate)
- No thread safety (single-threaded design)

---

## Future Directions

Key future features:

- **P3: Archetype Storage** - Optimization for 1000+ entities
- **Entity Relationships** - Parent-child hierarchies
- **World Replication** - Network synchronization helpers
