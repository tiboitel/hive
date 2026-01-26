from ..components import Position, AI, Player, Health
from ..command.commands import MoveCommand
from ..spatial import Spatial

class AiSystem:
    def move_toward_entity(self, store, entity, target):
        e = store.get(Position)[entity]
        t = store.get(Position)[target]

        dx = t.x - e.x
        dy = t.y - e.y
        if abs(dx) > abs(dy):
            dx = 1 if dx > 0 else -1
            dy = 0
        else:
            dy = 1 if dy > 0 else -1
            dx = 0
        
        cmd = MoveCommand(entity, dx, dy)
        return ([cmd]) 

    def think(self, store, entity):
        player = next(iter(store.get(Player)))
        for entity in store.get(AI):
            if entity in store.get(Health):
                return self.move_toward_entity(store, entity, player)

