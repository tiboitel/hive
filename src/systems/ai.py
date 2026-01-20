from ..components import Position

class AiSystem:
    def update(self, world, player, enemy):
        p = world.get(Position)[player]
        e = world.get(Position)[enemy]

        dx = p.x - e.x
        dy = p.y - e.y

        if abs(dx) > abs(dy):
            e.x += 1 if dx > 0 else -1
        else:
            e.y += 1 if dy > 0 else -1

