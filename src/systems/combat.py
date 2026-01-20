import random
from ..components import *

class CombatSystem:
    def attack(self, attacker, defender, world):
        atk = world.get(Combat)[attacker]
        hp = world.get(Health)[defender]

        dmg = max(0, random.randint(1, atk.atk - atk.defense // 2))
        hp.hp -= dmg
        return dmg

