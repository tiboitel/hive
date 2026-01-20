class World:
    def __init__(self):
        self.next_id = 0
        self.components = {}

    def create_entity(self):
        eid = self.next_id
        self.next_id += 1
        return eid

    def add(self, entity, component):
        self.components.setdefault(type(component), {})[entity] = component

    def get(self, component_type):
        return self.components.get(component_type, {})

