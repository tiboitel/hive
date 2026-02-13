"""Runtime: simple orchestration for World, Store and Dispatcher."""

from .core import World, CommandQueue
from .store import Store
from .command.dispatcher import CommandDispatcher
from .components import Destroyed


class Runtime:
    """Main runtime that orchestrates the ECS simulation."""

    def __init__(self):
        self._world = World()
        self._store = Store()
        self._dispatcher = CommandDispatcher()
        self._commands = CommandQueue()
        self.steps = 0

        # systems are registered by the host application or tests
        # runtime keeps a World container but does not hardcode domain systems

    @property
    def store(self):
        return self._store

    @property
    def world(self):
        return self._world

    def register(self, system, priority=0):
        """Register a system with optional priority."""
        self._world.add_system(system, priority)

    def step(self):
        """Execute one simulation step."""
        # Pass store and dispatcher to systems so they can access components
        # and dispatch commands. Host systems should accept signature
        # `update(store, dispatcher)`.
        self._world.step(self._store, self._dispatcher)
        self.steps += 1
        return self._cleanup()

    def _cleanup(self):
        """Remove destroyed entities."""
        destroyed = self._store.get(Destroyed)
        for entity in list(destroyed.keys()):
            self._store.destroy(entity)
