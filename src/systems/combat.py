import random
from ..components import *

class CombatSystem:
    def attack(self, cmd, store):
        atk = store.get(Combat)[cmd.entity]
        hp = store.get(Health)[cmd.target]

        dmg = max(0, random.randint(1, atk.atk - atk.defense // 2))
        hp.hp -= dmg
        if (hp.hp <= 0):
            store.add(cmd.target, Destroyed())
        return dmg

