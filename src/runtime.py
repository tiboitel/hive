"""Runtime: simple orchestration for World, Dispatcher and Command Routing."""

from typing import TypeVar, Type
from .core import World
from .command.dispatcher import CommandDispatcher
from .command.router import CommandRouter

T = TypeVar('T')


class Runtime:
    """Main runtime that orchestrates the ECS simulation.
    
    Runtime runs the simulation.
    World is the simulation.
    Store owns the simulation data (entities, components).
    Resources hold static data (config, assets).
    
    Example:
        runtime = Runtime()
        
        # Access world and its store
        e = runtime.world.create_entity()
        runtime.world.add_component(e, Position(0, 0))
        
        # Register systems
        runtime.register(MovementSystem())
        
        # Register command handlers
        runtime.router.register(MoveCommand, handle_move)
        
        # Run simulation
        runtime.step()
    """

    def __init__(self):
        self._world = World()
        self._dispatcher = CommandDispatcher()
        self._router = CommandRouter()
        self.steps = 0
        
        # Expose aliases for convenience
        self.event_bus = self._world.event_bus

    @property
    def world(self) -> World:
        """Access the simulation world."""
        return self._world
    
    @property
    def resources(self):
        """Access resources (static data like config, assets)."""
        return self._world.resources

    @property
    def router(self) -> CommandRouter:
        """Access the command router for registering command handlers."""
        return self._router

    def step(self) -> None:
        """Execute one simulation step.
        
        Steps:
        1. Run all systems (can emit commands via dispatcher)
        2. Route queued commands to registered handlers
        3. Increment step counter
        
        Entity cleanup (e.g., Destroyed component) should be handled
        by user-registered systems, not hardcoded in Runtime.
        """
        # Phase 1: Systems run and emit commands
        self._world.step(self._dispatcher)
        
        # Phase 2: Route commands to handlers
        commands = self._dispatcher.pop_all()
        if commands:
            self._router.handle_all(commands, self._world)
        
        self.steps += 1
