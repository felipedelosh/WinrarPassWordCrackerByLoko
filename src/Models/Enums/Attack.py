"""
FelipedelosH
2026

The way thats termites attack
"""
from enum import Enum, auto

class Attack(Enum):
    SEQUENTIAL = auto()
    RANDOM = auto()

    def __str__(self):
        return self.name
