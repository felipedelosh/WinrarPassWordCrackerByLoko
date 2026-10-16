"""
FelipedelosH
2026

Defines the lifecycle states of a password recovery job.
"""
# src/Models/Enums/WorkStatus.py
from enum import Enum, auto


class WorkStatus(Enum):
    NEW = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FOUND = auto()
    FAILED = auto()

    def __str__(self):
        return self.name
