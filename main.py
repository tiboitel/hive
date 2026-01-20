from src.world import World
from src.components import *
from src.spatial import Spatial
from src.systems.render import RenderSystem
from src.systems.movement import MovementSystem
from src.systems.combat import CombatSystem
from src.systems.ai import AiSystem

import sys
import os
import random

HEIGHT = 24
WIDTH = 48

def init_map() -> list: 
    game_map:list = []

    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            rand = random.randint(0, 100)

            if (x == 0 or x == WIDTH - 1) or (y == 0 or y == HEIGHT - 1):
                game_map.append("#")
            elif (rand <= 10):
                game_map.append("#")
            else:
                game_map.append(".")
    return game_map

def main():
    message_logs = list()


    render = RenderSystem() 
    movement = MovementSystem()
    combat = CombatSystem()
    ai = AiSystem()

    world = World()
    player = world.create_entity()

    world.add(player, Position(12, 6))
    world.add(player, Renderable("@"))
    world.add(player, Health(7, 7))
    world.add(player, Combat(4, 4))

    enemy = world.create_entity()
    world.add(enemy, Position(18, 12))
    world.add(enemy, Renderable("g"))
    world.add(enemy, Health(5, 5))
    world.add(enemy, Combat(5, 0))
    world.add(enemy, AI())

    game_map = init_map()
    current_turn = 0
    player_input = None

    while True:
        os.system("clear")
        print(f"Turn: {current_turn}\t Name: Volo l'Explorateur\nHP: {world.get(Health)[player].hp} / { world.get(Health)[player].max_hp } ")
        render.draw(world, game_map)

        player_input = input()
        dy = 0;
        dx = 0;
        if player_input == "w":
            dy -= 1
        elif player_input == "s":
            dy += 1
        elif player_input == "a":
            dx -= 1
        elif player_input == "d":
            dx += 1
        else:
            continue

        movement.update(world, dx, dy, player)

        if enemy in world.get(Health):
            if Spatial.adjacent(player, enemy, world):
                combat.attack(enemy, player, world)
            else:
                ai.update(world, player, enemy)

        current_turn += 1

if __name__ == "__main__":
    main()
