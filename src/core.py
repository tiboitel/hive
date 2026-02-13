from typing import Callable, Dict, List, Tuple


class System:
    def update(self, store, dispatcher):
        raise NotImplementedError


class World:
    """Lightweight world container that manages systems and execution order.

    Systems are stored as (priority, system_instance) and executed in
    increasing priority (lower numbers first).
    """

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


class CommandQueue:
    def __init__(self):
        self._queue = []

    def push(self, cmd):
        self._queue.append(cmd)

    def pop_all(self):
        items = list(self._queue)
        self._queue.clear()
        return items
