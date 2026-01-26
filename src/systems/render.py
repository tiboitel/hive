import os
from ..components import Position, Renderable, Health, Player

HEIGHT = 24
WIDTH = 48

class RenderSystem:
    def draw(self, store):
        player = next(iter(store.get(Player)))
        os.system("clear")
        print(f"Name: Volo l'Explorateur\nHP: {store.get(Health)[player].hp} / { store.get(Health)[player].max_hp } ")
        print()
        positions = store.get(Position)
        renderables = store.get(Renderable)

        entity_at = {
            (positions[e].x, positions[e].y): renderables[e].symbol
            for e in positions if e in renderables
        }

        for y in range(store.map.height):
            for x in range(store.map.width):
                print(entity_at.get((x, y), store.map.tiles[y * store.map.width + x]), end="")
            print()

