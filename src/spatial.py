from .components import Position
from .map import Map

class Spatial:
    
    @staticmethod
    def adjacent(a, b, store) -> bool:
        return abs(store.get(Position)[a].x - store.get(Position)[b].x) \
        + abs(store.get(Position)[a].y - store.get(Position)[b].y) == 1
    
    @staticmethod
    def entity_at(x, y, store):
        for e, pos in store.get(Position).items():
            if pos.x == x and pos.y == y:
                return e
        return None

    @staticmethod
    def blocked(x, y, store):
        if not (0 <= x < store.map.width and 0 <= y < store.map.height):
            return True
        return store.map.tiles[y * store.map.width + x] == "#"
    
    # @staticmethod
    # def in_range(a, b, r: int, store: World) -> bool:
    #    return abs(a.x - b.x) + abs(a.y - b.y) <= r

    # def in_sight(a, b, fov_map) -> bool:
    #    return fov_map[a.y][a.x] and fov_map[b.y][b.x]

