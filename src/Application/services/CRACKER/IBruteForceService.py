"""
FelipedelosH
2026
"""
# src\Application\services\CRACKER\IBruteForceService.py
from abc import ABC, abstractmethod


class IBruteForceService(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass
