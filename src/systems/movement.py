from ..components import *

class MovementSystem:
    def update(self, world, dx, dy, entity):
        pos = world.get(Position)[entity]
        pos.x += dx
        pos.y += dy

