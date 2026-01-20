from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Renderable:
    symbol: str

@dataclass
class Health:
    max_hp: int
    hp: int

@dataclass
class Combat:
    atk: int
    defense: int

@dataclass
class AI:
    pass
