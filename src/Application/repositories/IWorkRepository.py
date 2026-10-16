"""
FelipedelosH
2026

Contract for password recovery job persistence.
"""
# src\Application\repositories\IWorkRepository.py
from abc import ABC, abstractmethod
from typing import Optional
from src.Models.Entities.WorkState import WorkState


class IWorkRepository(ABC):
    @abstractmethod
    def load(self) -> Optional[WorkState]:
        pass

    @abstractmethod
    def save(self, state: WorkState) -> None:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

    @abstractmethod
    def archive(self) -> Optional[str]:
        pass
