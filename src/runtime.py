from .command.dispatcher import CommandDispatcher
from .systems.movement import MovementSystem
from .systems.combat import CombatSystem
from .systems.ai import AiSystem
from .systems.render import RenderSystem
from .components import AI, Health, Destroyed
from .store import Store

class Runtime:
    def __init__(self):
        self.systems = {}
        self.store = Store()
        self.dispatcher = CommandDispatcher()
        self.register(MovementSystem)
        self.register(CombatSystem)
        self.register(AiSystem)
        self.register(RenderSystem)
        self.steps = 0
        self.running = True
        
    def register(self, system):
        self.systems[system] = system()

    def step(self):
        for entity in self.store.get(AI):
            if entity in self.store.get(Health) and self.store.get(Health)[entity].hp > 0:
                cmds = self.systems[AiSystem].think(self.store, self.dispatcher)
                if cmds is not None:
                    for cmd in cmds:
                        self.dispatcher.dispatch(cmd)
        self.dispatcher.process(self)
        self.systems[RenderSystem].draw(self.store)
        self.steps + 1
        return self.cleanup()

    def cleanup(self):
        entities = list(self.store.get(Destroyed))
        for entity in entities:
            self.store.destroy(entity)
