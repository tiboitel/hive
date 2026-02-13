from src.runtime import Runtime
from src.components import *
from src.spatial import Spatial
from src.command.commands import MoveCommand
from src.command.dispatcher import CommandDispatcher
from src.systems.render import RenderSystem
from src.systems.ai import AiSystem

import time

def main():
    runtime = Runtime()
    store = runtime.store

    # todo: maps should be separated from Store
    player = store.create_entity()

    store.add(player, Position(12, 6))
    store.add(player, Renderable("@"))
    store.add(player, Health(10, 10))
    store.add(player, Combat(3, 3))
    store.add(player, AI())

    enemy = store.create_entity()
    store.add(enemy, Position(18, 12))
    store.add(enemy, Renderable("g"))
    store.add(enemy, Health(2, 2))
    store.add(enemy, Combat(2, 1))
    store.add(enemy, AI())

    enemy = store.create_entity()
    store.add(enemy, Position(22, 13))
    store.add(enemy, Renderable("g"))
    store.add(enemy, Health(2, 2))
    store.add(enemy, Combat(2, 1))
    store.add(enemy, AI())

    player_input = None
    while True:
        runtime.step()
        print(f"Step: {runtime.steps}")
        time.sleep(0.5)
        '''player_input = input()
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
        
        cmd = MoveCommand(player, dx, dy)
        runtime.dispatcher.dispatch(cmd)'''

if __name__ == "__main__":
    main()
