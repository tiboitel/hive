"""Example host application using the generic ECS framework.

Demonstrates creating a runtime, registering two minimal systems,
creating entities and components, then stepping the world.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.runtime import Runtime
from src.core import System
from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Renderable:
    symbol: str

class ExampleRender(System):
    def update(self, store, dispatcher):
        positions = store.get(Position)
        renderables = store.get(Renderable)
        for eid, pos in positions.items():
            if eid in renderables:
                print(f"Entity {eid} at ({pos.x},{pos.y}) => {renderables[eid].symbol}")

def main():
    runtime = Runtime()
    # register a simple render system
    runtime.register(ExampleRender(), priority=10)

    store = runtime.store

    # create two entities
    a = store.create_entity()
    b = store.create_entity()

    store.add(a, Position(1, 2))
    store.add(a, Renderable("A"))

    store.add(b, Position(4, 5))
    store.add(b, Renderable("B"))

    # run a few steps
    for _ in range(3):
        runtime.step()

if __name__ == "__main__":
    main()
