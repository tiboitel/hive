from dataclasses import dataclass

@dataclass(frozen=True)
class MoveCommand:
    entity: int
    dx: int
    dy: int

@dataclass(frozen=True)
class BumpCommand:
    entity: int
    target: int

@dataclass(frozen=True)
class AttackCommand:
    entity:int
    target: int
