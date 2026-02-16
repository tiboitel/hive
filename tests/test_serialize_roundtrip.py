import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass
from src.core import World
from src.serialize import snapshot, load_into_world


@dataclass
class P:
    x: int
    y: int


def test_snapshot_and_load_roundtrip(tmp_path):
    w = World()
    e = w.create_entity()
    w.add_component(e, P(1, 2))

    snap = snapshot(w)
    pfile = tmp_path / "snap.json"
    import json
    with open(pfile, 'w') as f:
        json.dump(snap, f)

    # load into a fresh world
    w2 = World()
    with open(pfile, 'r') as f:
        data = json.load(f)
    load_into_world(data, w2)

    comps = w2.get_components(P)
    assert int(list(comps.keys())[0]) == e
    comp = list(comps.values())[0]
    assert comp.x == 1 and comp.y == 2
