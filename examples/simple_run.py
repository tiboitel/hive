"""Example host application using the generic ECS framework.

Demonstrates creating a runtime, registering two minimal systems,
creating entities and components, then stepping the world.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.runtime import Runtime
from src.core import System, World
from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Renderable:
    symbol: str

class ExampleRender(System):
    def update(self, world: World, dispatcher):
        positions = world.store.get_components(Position)
        renderables = world.store.get_components(Renderable)
        for eid, pos in positions.items():
            if eid in renderables:
                print(f"Entity {eid} at ({pos.x},{pos.y}) => {renderables[eid].symbol}")

def main():
    runtime = Runtime()
    # register a simple render system

    world = runtime.world
    world.register(ExampleRender(), priority=10)

    # create two entities
    a = world.create_entity()
    b = world.create_entity()

    world.add_component(a, Position(1, 2))
    world.add_component(a, Renderable("A"))

    world.add_component(b, Position(4, 5))
    world.add_component(b, Renderable("B"))

    # run a few steps
    for _ in range(3):
        runtime.step()

if __name__ == "__main__":
    main()
