from ..components import Position, Renderable

HEIGHT = 24
WIDTH = 48

class RenderSystem:
    def draw(self, world, game_map):
        positions = world.get(Position)
        renderables = world.get(Renderable)

        entity_at = {
            (positions[e].x, positions[e].y): renderables[e].symbol
            for e in positions if e in renderables
        }

        for y in range(HEIGHT):
            for x in range(WIDTH):
                print(entity_at.get((x, y), game_map[y * WIDTH + x]), end="")
            print()

