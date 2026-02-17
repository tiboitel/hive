# Hive API Reference

Complete reference for the Hive ECS micro-framework public API.

## Table of Contents

- [Runtime](#runtime)
- [World](#world)
- [System](#system)
- [Store](#store)
- [EventBus](#eventbus)
- [ResourceRegistry](#resourceregistry)
- [CommandDispatcher](#commanddispatcher)
- [CommandRouter](#commandrouter)
- [Serialization](#serialization)

---

## Runtime

Main orchestration class that coordinates World, CommandDispatcher, and CommandRouter.

```python
from hive import Runtime

runtime = Runtime()
```

### Attributes

- `world: World` - Access the simulation world
- `resources: ResourceRegistry` - Access static resources
- `router: CommandRouter` - Access command router for registering handlers
- `event_bus: EventBus` - Event bus alias for convenience
- `steps: int` - Number of simulation steps executed

### Methods

#### `step() -> None`

Execute one simulation step:
1. Run all registered systems
2. Route queued commands to registered handlers
3. Increment step counter

---

## World

Simulation container that owns Store, systems, event bus, and resources.

```python
from hive import World

world = World()
```

### Attributes

- `store: Store` - Entity/component storage
- `event_bus: EventBus` - Event pub/sub system
- `resources: ResourceRegistry` - Resource storage

### Methods

#### Entity & Component Management

**`create_entity() -> int`**
Create a new entity and return its ID.

**`destroy_entity(entity: int) -> None`**
Destroy an entity and all its components. ID is recycled.

**`add_component(entity: int, component) -> None`**
Add a component to an entity. Overwrites existing component of same type.

**`get_components(component_type: Type) -> Dict[int, Any]`**
Get all components of a specific type. Returns empty dict if none exist.

**`has_component(entity: int, component_type: Type) -> bool`**
Check if an entity has a specific component.

**`remove_component(entity: int, component_type: Type) -> bool`**
Remove a component from an entity. Returns True if removed, False if not present.

#### Querying

**`query_entities(*component_types: Type) -> Iterator[int]`**
Yield entity IDs that have all requested component types. Deterministic (sorted order).

**`query(*component_types: Type) -> Iterator[Tuple[int, ...]]`**
Yield tuples of (entity_id, component1, component2, ...) for matching entities.

```python
for eid, pos, vel in world.query(Position, Velocity):
    print(f"Entity {eid} at ({pos.x}, {pos.y})")
```

#### System Management

**`register(system: System, priority: int = 0) -> None`**
Register a system with optional priority. Lower priority runs first.

**`step(dispatcher=None) -> None`**
Execute all registered systems in priority order. Used internally by Runtime.

#### Serialization

**`snapshot() -> dict`**
Create a JSON-serializable snapshot of the world state.

---

## System

Base class for ECS systems. Implement game logic by processing entities with specific components.

```python
from hive import System
from hive.core import World

class MovementSystem(System):
    def update(self, world: World, dispatcher) -> None:
        for eid, pos, vel in world.query(Position, Velocity):
            pos.x += vel.dx
            pos.y += vel.dy
```

### Methods

**`update(world: World, dispatcher) -> None`**
Execute system logic. Override this method in subclasses.

- `world`: World instance for accessing store, events, resources
- `dispatcher`: CommandDispatcher for emitting commands

---

## Store

Entity and component storage. Owns the data layer of the ECS.

```python
from hive import Store

store = Store()
```

### Methods

**`create_entity() -> int`**
Create a new entity with recycled ID if available.

**`destroy_entity(entity: int) -> None`**
Destroy entity and all its components. ID recycled unless free list too large.

**`add_component(entity: int, component) -> None`**
Add a component to an entity.

**`get_components(component_type: Type) -> Dict[int, Any]`**
Get all components of a specific type.

**`has_component(entity: int, component_type: Type) -> bool`**
Check if entity has specific component type.

**`remove_component(entity: int, component_type: Type) -> bool`**
Remove component from entity.

**`query_entities(*component_types: Type) -> Iterator[int]`**
Yield entity IDs with all requested component types (intersection).

**`query(*component_types: Type) -> Iterator[Tuple[int, ...]]`**
Yield tuples of (entity_id, comp1, comp2, ...) for matching entities.

---

## EventBus

Synchronous publish/subscribe event system for decoupled communication.

```python
from hive import EventBus

bus = EventBus()
```

### Methods

**`on(event_type, handler) -> tuple`**
Subscribe to an event type. Returns subscription token for unsubscribing.

```python
def on_player_died(event, world, dispatcher):
    print(f"Player {event.player_id} died!")

token = bus.on(PlayerDiedEvent, on_player_died)
```

**`off(token) -> bool`**
Unsubscribe using token from `on()`. Returns True if removed.

**`emit(event, world=None, dispatcher=None) -> None`**
Emit an event to all subscribers. Exceptions in handlers are logged but don't stop others.

```python
bus.emit(PlayerDiedEvent(player_id=42), world, dispatcher)
```

---

## ResourceRegistry

Lightweight storage for global/shared objects (config, random seed, assets).

```python
from hive import ResourceRegistry

resources = ResourceRegistry()
```

### Methods

**`register(resource: T) -> None`**
Register a resource using its type as key.

```python
resources.register(GameConfig(difficulty="hard"))
```

**`get(resource_type: Type[T]) -> T`**
Get resource by type. Raises KeyError if not found.

```python
config = resources.get(GameConfig)
```

**`get_or(resource_type: Type[T], default: T) -> T`**
Get resource with default fallback.

**`has(resource_type: Type[T]) -> bool`**
Check if resource type is registered.

**`all() -> dict`**
Return copy of all registered resources.

---

## CommandDispatcher

Minimal, generic command queue. Systems emit commands; host processes them.

```python
from hive import CommandDispatcher

dispatcher = CommandDispatcher()
```

### Methods

**`dispatch(command) -> None`**
Queue a command.

**`pop_all() -> list`**
Remove and return all queued commands.

**`pop() -> Any`**
Remove and return the next command (FIFO).

**`process(handler: callable) -> None`**
Process all queued commands with the provided handler.

```python
dispatcher.process(lambda cmd: print(f"Handling: {cmd}"))
```

---

## CommandRouter

Type-safe command routing without isinstance checks.

```python
from hive import CommandRouter

router = CommandRouter()
router.register(MoveCommand, handle_move)
router.register(AttackCommand, handle_attack)

# Route commands
router.route(cmd, world)
stats = router.handle_all(commands, world)
```

### Methods

**`register(cmd_type: Type, handler: Callable) -> None`**
Register a handler for a command type. Raises ValueError if already registered.

**`unregister(cmd_type: Type) -> bool`**
Remove handler registration. Returns True if removed.

**`route(cmd: Any, world) -> bool`**
Route single command to its handler. Returns True if routed.

**`handle_all(commands, world) -> Dict[Type, int]`**
Process multiple commands. Returns stats dict of {cmd_type: count}.

**`has_handler(cmd_type: Type) -> bool`**
Check if handler is registered for command type.

**`registered_types() -> list`**
Return list of registered command types.

---

## Serialization

World state serialization/deserialization.

### Functions

**`snapshot(world) -> dict`**
Create JSON-serializable snapshot including:
- Next entity ID
- All components (dataclasses supported automatically)
- Serializable resources

**`load_into_world(snapshot_obj, world) -> None`**
Load snapshot into existing World instance.

**`register_serializer(type_, to_dict, from_dict) -> None`**
Register custom serializers for non-dataclass components.

```python
from hive.serialize import register_serializer

register_serializer(
    MyComponent,
    lambda c: {"value": c.value},
    lambda d: MyComponent(d["value"])
)
```

---

## Quick Reference

### Common Patterns

```python
from dataclasses import dataclass
from hive import Runtime, System

# Define components
@dataclass
class Position:
    x: int
    y: int

@dataclass
class Velocity:
    dx: int
    dy: int

# Define system
class MovementSystem(System):
    def update(self, world, dispatcher):
        for eid, pos, vel in world.query(Position, Velocity):
            pos.x += vel.dx
            pos.y += vel.dy

# Setup runtime
runtime = Runtime()
runtime.world.register(MovementSystem(), priority=0)

# Create entities
e = runtime.world.create_entity()
runtime.world.add_component(e, Position(0, 0))
runtime.world.add_component(e, Velocity(1, 1))

# Run simulation
runtime.step()
```

### Priority Ordering

Systems execute in priority order (lower = earlier):

```python
world.register(InputSystem(), priority=-100)   # First
world.register(PhysicsSystem(), priority=0)    # Second
world.register(RenderSystem(), priority=100)   # Last
```

### Events

```python
@dataclass
class DamageEvent:
    target: int
    amount: int

# Subscribe
world.event_bus.on(DamageEvent, lambda e, w, d: print(f"Damage: {e.amount}"))

# Emit from system
world.event_bus.emit(DamageEvent(target=eid, amount=10), world, dispatcher)
```

### Resources

```python
@dataclass
class GameConfig:
    tick_rate: int = 60

runtime.resources.register(GameConfig(tick_rate=30))
config = runtime.resources.get(GameConfig)
```
