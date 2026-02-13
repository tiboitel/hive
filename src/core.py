from typing import Callable, Dict, List, Tuple


class System:
    def update(self, store, dispatcher):
        raise NotImplementedError


class World:
    """Small world container: systems, entities and components."""

    def __init__(self):
        self._systems: List[Tuple[int, object]] = []
        self._next_id = 0
        self._components: Dict[type, Dict[int, object]] = {}

    def add_system(self, system, priority: int = 0):
        self._systems.append((priority, system))
        self._systems.sort(key=lambda t: t[0])

    def step(self, store=None, dispatcher=None):
        for _, system in list(self._systems):
            # systems implement their own update signature
            method = getattr(system, "update", None)
            if method is None:
                continue
            method(store, dispatcher)

    # Entity/component API
    def create_entity(self) -> int:
        eid = self._next_id
        self._next_id += 1
        return eid

    def add_component(self, entity: int, component) -> None:
        self._components.setdefault(type(component), {})[entity] = component

    def get_components(self, component_type):
        return self._components.get(component_type, {})

    def has_component(self, entity: int, component_type) -> bool:
        return entity in self._components.get(component_type, {})

    def destroy_entity(self, entity: int) -> None:
        for comp in self._components.values():
            comp.pop(entity, None)

    # Query APIs
    def query_entities(self, *component_types):
        """Yield entity ids that have all requested component types.

        Deterministic: yields ids in ascending order.
        """
        if not component_types:
            return iter(())
        sets = [set(self._components.get(t, {}).keys()) for t in component_types]
        if not sets:
            return iter(())
        ids = set.intersection(*sets)
        for eid in sorted(ids):
            yield eid

    def query(self, *component_types):
        """Yield tuples (entity, comp1, comp2, ...) for matching entities."""
        for eid in self.query_entities(*component_types):
            yield (eid,) + tuple(self._components[t][eid] for t in component_types)


class CommandQueue:
    def __init__(self):
        self._queue = []

    def push(self, cmd):
        self._queue.append(cmd)

    def pop_all(self):
        items = list(self._queue)
        self._queue.clear()
        return items
