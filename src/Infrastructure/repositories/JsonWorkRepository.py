"""
FelipedelosH
2026

JSON implementation of password recovery job persistence.
"""
# src\Infrastructure\repositories\JsonWorkRepository.py
import os
import json
from dataclasses import asdict
from datetime import datetime
from typing import Optional
from src.Application.repositories.IWorkRepository import IWorkRepository
from src.Models.Entities.WorkState import WorkState
from src.Models.Enums.WorkStatus import WorkStatus


class JsonWorkRepository(IWorkRepository):
    def __init__(self, work_path: str):
        self.work_path = work_path

    def exists(self) -> bool:
        return os.path.isfile(self.work_path)

    def load(self) -> Optional[WorkState]:
        if not self.exists():
            return None

        with open(self.work_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if data.get("version") != 1:
            raise ValueError("Unsupported work.json version.")

        data["status"] = WorkStatus[data["status"]]

        return WorkState(**data)

    def save(self, state: WorkState) -> None:
        directory = os.path.dirname(os.path.abspath(self.work_path))
        os.makedirs(directory, exist_ok=True)

        data = asdict(state)
        data["status"] = state.status.name

        temp_path = self.work_path + ".tmp"

        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_path, self.work_path)

    def archive(self) -> Optional[str]:
        if not self.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        directory = os.path.dirname(self.work_path)
        archive_path = os.path.join(
            directory,
            f"work.archived.{timestamp}.json"
        )

        os.replace(self.work_path, archive_path)

        return archive_path

    def backupCorrupt(self) -> Optional[str]:
        """Renombra work.json a work.corrupt.{timestamp}.json preservando el original."""
        if not self.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        directory = os.path.dirname(self.work_path)
        corrupt_path = os.path.join(
            directory,
            f"work.corrupt.{timestamp}.json"
        )

        os.replace(self.work_path, corrupt_path)

        return corrupt_path
