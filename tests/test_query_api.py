import sys, os
from dataclasses import dataclass

# Ensure project root is on sys.path so `src` package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import World


@dataclass
class A:
    v: int


@dataclass
class B:
    s: str


def test_query_and_query_entities_basic():
    w = World()
    e1 = w.create_entity()
    e2 = w.create_entity()
    e3 = w.create_entity()

    w.add_component(e1, A(1))
    w.add_component(e1, B("x"))
    w.add_component(e2, A(2))
    w.add_component(e3, B("z"))

    assert list(w.query_entities(A)) == [e1, e2]
    assert list(w.query_entities(B)) == [e1, e3]
    assert list(w.query_entities(A, B)) == [e1]

    results = list(w.query(A, B))
    assert results == [(e1, w.get_components(A)[e1], w.get_components(B)[e1])]

    w.destroy_entity(e1)
    assert e1 not in w.get_components(A)
    assert list(w.query_entities(A, B)) == []
