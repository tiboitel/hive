"""Test entity ID recycling functionality."""
import sys, os
from dataclasses import dataclass
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import World
from src.store import Store


def test_store_entity_recycling():
    """Test that destroyed entity IDs are recycled."""
    store = Store()
    
    # Create entities
    e1 = store.create_entity()
    e2 = store.create_entity()
    e3 = store.create_entity()
    
    assert e1 == 0
    assert e2 == 1
    assert e3 == 2
    
    # Destroy middle entity
    store.destroy_entity(e2)
    
    # Next entity should reuse e2's ID
    e4 = store.create_entity()
    assert e4 == e2, f"Expected recycled ID {e2}, got {e4}"
    
    # Next should be new
    e5 = store.create_entity()
    assert e5 == 3
    
    print("✓ Entity recycling works correctly")


def test_store_safety_limit():
    """Test that free ID list has a safety limit."""
    store = Store()
    
    # Create many entities
    entities = []
    for i in range(Store.MAX_FREE_IDS + 10):
        e = store.create_entity()
        entities.append(e)
    
    # Destroy them all
    for e in entities:
        store.destroy_entity(e)
    
    # Free list should be capped at MAX_FREE_IDS
    assert len(store._free_ids) == Store.MAX_FREE_IDS, \
        f"Expected {Store.MAX_FREE_IDS} free IDs, got {len(store._free_ids)}"
    
    print("✓ Free ID safety limit works correctly")


def test_world_delegation():
    """Test that World properly delegates to Store."""
    world = World()
    
    e1 = world.create_entity()
    e2 = world.create_entity()
    
    # Destroy via world
    world.destroy_entity(e1)
    
    # Should be recycled
    e3 = world.create_entity()
    assert e3 == e1
    
    print("✓ World properly delegates to Store")


def test_ecs_semantics_empty_query():
    """Test that queries return empty for missing components (ECS semantics)."""
    world = World()
    
    @dataclass
    class NonExistent:
        pass
    
    # Query for non-existent component should return empty, not raise
    result = list(world.store.query_entities(NonExistent))
    assert result == []
    
    result = list(world.store.query(NonExistent))
    assert result == []
    
    print("✓ ECS semantics: empty results for missing components")


if __name__ == "__main__":
    test_store_entity_recycling()
    test_store_safety_limit()
    test_world_delegation()
    test_ecs_semantics_empty_query()
    
    print("\nAll Store/World tests passed!")
