"""
FelipedelosH
2026
"""
# src\Application\services\CRACKER\ISequentialBruteForceService.py
from abc import ABC, abstractmethod


class ISequentialBruteForceService(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass
