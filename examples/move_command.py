"""Playful example showing command usage with the ECS framework.

Defines a simple `Move` command, a system that emits moves each tick and a
system that handles commands to mutate `Position` components. Shows how a
host application can use the framework's dispatcher without adding domain
logic to the framework itself.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass
from src.runtime import Runtime
from src.core import System


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


class Emitter(System):
    """Emits a Move command for the controlled entity each tick."""

    def __init__(self, entity, pattern=None):
        self.entity = entity
        self.tick = 0
        self.pattern = pattern or [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def update(self, store, dispatcher):
        dx, dy = self.pattern[self.tick % len(self.pattern)]
        dispatcher.dispatch(Move(self.entity, dx, dy))
        self.tick += 1


class CommandHandler(System):
    """Handles Move commands pulled from the dispatcher."""

    def update(self, store, dispatcher):
        for cmd in dispatcher.pop_all():
            if isinstance(cmd, Move):
                comps = store.get(Position)
                if cmd.entity in comps:
                    pos = comps[cmd.entity]
                    pos.x += cmd.dx
                    pos.y += cmd.dy


class Printer(System):
    def update(self, store, dispatcher):
        positions = store.get(Position)
        renderables = store.get(Renderable)
        out = []
        for eid in sorted(positions.keys()):
            pos = positions[eid]
            sym = renderables.get(eid)
            ch = sym.symbol if sym else "?"
            out.append(f"{ch}@({pos.x},{pos.y})")
        print(" | ".join(out))


def main():
    runtime = Runtime()
    store = runtime.store

    # spawn a playful entity
    e = store.create_entity()
    store.add(e, Position(0, 0))
    store.add(e, Renderable("P"))

    # register systems: emitter -> handler -> printer
    runtime.register(Emitter(e), priority=5)
    runtime.register(CommandHandler(), priority=10)
    runtime.register(Printer(), priority=20)

    print("Playful command demo (5 ticks)")
    for _ in range(5):
        runtime.step()


if __name__ == "__main__":
    main()
