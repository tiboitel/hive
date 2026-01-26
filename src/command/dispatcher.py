from collections import deque
from ..systems.movement import MovementSystem
from ..systems.combat import CombatSystem
from ..command.commands import MoveCommand, BumpCommand, AttackCommand

class CommandDispatcher:
    def __init__(self):
        self.queue = deque()

    def dispatch(self, command):
        self.queue.append(command)

    def process(self, runtime):
        if not self.queue:
            return False
        while len(self.queue):
            command = self.queue.popleft()
            self.route(command, runtime)
        return True

    def route(self, command, runtime):
        if isinstance(command, MoveCommand):
            cmds = runtime.systems[MovementSystem].update(command, runtime.store)
            if cmds is not None:
                for cmd in cmds:
                    runtime.dispatcher.dispatch(cmd)
        if isinstance(command, BumpCommand):
            self.dispatch(AttackCommand(command.entity, command.target))
        if isinstance(command, AttackCommand):
            runtime.systems[CombatSystem].attack(command, runtime.store)
