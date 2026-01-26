import random
from .components import *
from .map import Map

class Store:
    def __init__(self):
        self.next_id = 0
        self.components = {}
        self.map = Map(48, 24)
        self.map.generate()
        
    def create_entity(self) -> int:
        eid = self.next_id
        self.next_id += 1
        return eid

    def add(self, entity, component):
        self.components.setdefault(type(component), {})[entity] = component

    def get(self, component_type):
        return self.components.get(component_type, {})

    def destroy(self, entity: int):
        for component in self.components.values():
            component.pop(entity, None)







