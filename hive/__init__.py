"""Hive - A minimal, generic ECS micro-framework."""

from .runtime import Runtime
from .core import World, System
from .store import Store
from .resources import ResourceRegistry
from .events import EventBus
from .command.dispatcher import CommandDispatcher
from .command.router import CommandRouter

__version__ = "0.0.8"

__all__ = [
    "Runtime",
    "World",
    "System",
    "Store",
    "ResourceRegistry",
    "EventBus",
    "CommandDispatcher",
    "CommandRouter",
]
