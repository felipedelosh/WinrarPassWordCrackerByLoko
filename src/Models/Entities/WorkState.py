"""
FelipedelosH
2026

Represents the persistent state of a password recovery job.
"""
# src/Models/WorkState.py
from dataclasses import dataclass, field
from typing import Optional
from src.Models.Enums.WorkStatus import WorkStatus


@dataclass
class WorkState:
    version: int = 1
    # Identity
    rar_file: str = ""
    rar_sha256: str = ""
    rar_size_bytes: int = 0
    charset: str = ""
    min_len: int = 0
    max_len: int = 0
    attack_mode: str = "SEQUENTIAL"

    # State
    status: WorkStatus = WorkStatus.NEW
    password_found: bool = False

    # Progress
    completed_colonies: list[int] = field(default_factory=list)
    current_colony: Optional[int] = None
    current_colony_index: int = -1
    total_combinations_tried: int = 0

    # Metadata
    total_colonies: int = 0
    total_combinations: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    flush_interval: int = 100
