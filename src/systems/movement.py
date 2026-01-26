from ..components import Position
from ..spatial import Spatial
from ..command.commands import BumpCommand

class MovementSystem:
    def update(self, cmd, store):
        pos = store.get(Position)[cmd.entity]
        dest_x = pos.x + cmd.dx
        dest_y = pos.y + cmd.dy

        if Spatial.blocked(dest_x, dest_y, store):
            return

        target = Spatial.entity_at(dest_x, dest_y, store)
        if target is not None:
            cmd = [BumpCommand(cmd.entity, target)]
            return cmd

        pos.x = dest_x
        pos.y = dest_y

