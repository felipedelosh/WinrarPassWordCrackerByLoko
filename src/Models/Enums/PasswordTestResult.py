"""
FelipedelosH
2026

Result of testing a single password candidate against a RAR archive.
Distinguishes a finished check (correct/incorrect) from a technical
failure (error) so that progress is only advanced on finalized checks.
"""
# src/Models/Enums/PasswordTestResult.py
from enum import Enum, auto


class PasswordTestResult(Enum):
    CORRECT = auto()
    INCORRECT = auto()
    ERROR = auto()
