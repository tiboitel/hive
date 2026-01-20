from .world import World
from .components import *

class Spatial:
    
    @staticmethod
    def adjacent(a, b, world: World) -> bool:
        return abs(world.get(Position)[a].x - world.get(Position)[b].x) \
        + abs(world.get(Position)[a].y - world.get(Position)[b].y) == 1

    # @staticmethod
    # def in_range(a, b, r: int, world: World) -> bool:
    #    return abs(a.x - b.x) + abs(a.y - b.y) <= r

    # def in_sight(a, b, fov_map) -> bool:
    #    return fov_map[a.y][a.x] and fov_map[b.y][b.x]

