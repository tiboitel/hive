"""Entity and component storage.

This module wraps the core ECS World for backward compatibility.
"""

from .core import World


class Store:
    """Backward-compatible wrapper around World."""

    def __init__(self):
        self._world = World()

    @property
    def world(self) -> World:
        return self._world

    def create_entity(self) -> int:
        return self._world.create_entity()

    def add(self, entity: int, component) -> None:
        self._world.add_component(entity, component)

    def get(self, component_type):
        return self._world.get_components(component_type)

    def query_entities(self, *component_types):
        return self._world.query_entities(*component_types)

    def query(self, *component_types):
        return self._world.query(*component_types)

    def has_component(self, entity: int, component_type) -> bool:
        return self._world.has_component(entity, component_type)

    def destroy(self, entity: int) -> None:
        self._world.destroy_entity(entity)
