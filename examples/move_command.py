"""Playful example showing command usage with built-in CommandRouter.

Demonstrates the Command Router pattern: register command handlers by type
with the runtime, and commands are automatically routed after each step.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass
from src.runtime import Runtime
from src.core import System, World


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Renderable:
    symbol: str


@dataclass(frozen=True)
class Move:
    entity: int
    dx: int
    dy: int


class Movement(System):
    """Emits a Move command for the controlled entity each tick."""

    def __init__(self, pattern=None):
        self.tick = 0
        self.pattern = pattern or [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def update(self, world: World, dispatcher):
        for entity in world.store.query_entities(Position):
            dx, dy = self.pattern[self.tick % len(self.pattern)]
            dispatcher.dispatch(Move(entity, dx, dy))
        self.tick += 1

    def handle_move(self, cmd: Move, world: World) -> None:
        """Handler for Move commands.
        
        Receives the command and the world instance.
        Access components through the world's component storage.
        """
        comps = world.store.get_components(Position)
        if cmd.entity in comps:
            pos = comps[cmd.entity]
            pos.x += cmd.dx
            pos.y += cmd.dy


class Renderer(System):
    def update(self, world: World, dispatcher):
        positions = world.store.get_components(Position)
        renderables = world.store.get_components(Renderable)
        out = []
        for eid in sorted(positions.keys()):
            pos = positions[eid]
            sym = renderables.get(eid)
            ch = sym.symbol if sym else "?"
            out.append(f"{ch}@({pos.x},{pos.y})")
        print(" | ".join(out))


def main():
    runtime = Runtime()
    world = runtime.world

    # spawn a playful entity
    e = world.create_entity()
    world.add_component(e, Position(0, 0))
    world.add_component(e, Renderable("P"))
   
    # Additional commands can be registered here:
    # runtime.router.register(JumpCommand, handle_jump)
    # runtime.router.register(AttackCommand, handle_attack)

    # register systems: emitter -> printer
    # Commands are auto-routed after systems run - no RouterSystem needed!
    movement = Movement()
    world.register(movement, priority=5)
    world.register(Renderer(), priority=20)

    # Register command handler with the runtime's router
    runtime.router.register(Move, movement.handle_move)
 
    print("Playful command demo with built-in router (5 ticks)")
    print("Commands are automatically routed to handlers after each step.")
    for _ in range(5):
        runtime.step()


if __name__ == "__main__":
    main()
