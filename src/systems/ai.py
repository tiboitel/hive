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
        return (cmd) 

    def think(self, store):
        # Choose a player: prefer a Player component, otherwise fall back to Health
        cmds = []
        for entity in store.get(AI):
            if entity in store.get(Health) and store.get(Health)[entity].hp > 0:
                if len(store.get(Player)) > 0:
                    target = next(iter(store.get(Player)))
                else:
                    target = next(
                        (e for e in store.get(Health) if e != entity),
                        None
                    )
                if target is not None:
                    cmds.append(self.move_toward_entity(store, entity, target))
        return cmds
