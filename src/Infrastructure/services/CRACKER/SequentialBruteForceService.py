"""
FelipedelosH
2026
"""
# src\Infrastructure\services\CRACKER\SequentialBruteForceService.py
import os
from datetime import datetime
from src.Application.repositories.IWorkRepository import IWorkRepository
from src.Models.Enums.WorkStatus import WorkStatus
from src.Models.Enums.PasswordTestResult import PasswordTestResult
from src.Application.services.CRACKER.IBruteForceService import IBruteForceService
from src.Infrastructure.services.PasswordCombinationGenerator import PasswordCombinationGenerator
from src.Infrastructure.services.TermiteService import TermiteService
from src.Infrastructure.services.WinrarService import WinrarService
from src.Infrastructure.services.BeautifulPrinter import BeautifulPrinter


class TermiteCheckError(Exception):
    """Raised when a termite check fails with a transient technical error.

    Progress must NOT advance: the candidate was not confirmed as incorrect,
    so on resume it has to be retried. Carries the index (never the password).
    """
    def __init__(self, index: int):
        super().__init__(f"TERMITE_CHECK_ERROR::INDEX::{index}")
        self.index = index


class SequentialBruteForceService(IBruteForceService):
    def __init__(self, rar_path, unrar_path, charset, min_len, max_len, temp_path, output_path, work_repository, logger):
        self.rar_path = rar_path
        self.unrar_path = unrar_path
        self.charset = charset
        self.min_len = min_len
        self.max_len = max_len
        self.temp_path = temp_path
        self.output_path = output_path
        self.work_repository = work_repository
        self.logger = logger


    def execute(self):
        """Execute the sequential colony workflow, resuming from work.json if possible."""
        self._validate_inputs()
        total = PasswordCombinationGenerator.countTotal(
            self.charset, self.min_len, self.max_len
        )
        self.logger.info("SequentialBruteForceService::execute::TRY")
        self.logger.info(f"SequentialBruteForceService::execute::CHARS::TOTAL::{len(self.charset)}")
        self.logger.info(f"SequentialBruteForceService::execute::CHARS::{self.charset}")
        self.logger.info(f"SequentialBruteForceService::execute::TOTAL_COMBINATIONS::{total:,}")
        self.logger.info(f"SequentialBruteForceService::execute::LEN_FROM::{self.min_len}::LEN_TO::{self.max_len}")
        print("\n=========TERMITES INIT=========")
        print("PRESS: (Ctrl+C) TO STOP\n")

        # LOAD WORK (Controller already created/verified and saved it)
        work = self.work_repository.load()
        if work is None:
            self.logger.error("SequentialBruteForceService::execute::WORK_NOT_FOUND")
            return False

        # Terminal states: do not re-execute
        if work.status in (WorkStatus.FOUND, WorkStatus.COMPLETED, WorkStatus.FAILED):
            self.logger.info(
                f"SequentialBruteForceService::execute::WORK_ALREADY_FINISHED::STATUS::{work.status}"
            )
            return False

        if work.status == WorkStatus.RUNNING:
            self.logger.warn("SequentialBruteForceService::execute::PREVIOUS_RUN_NOT_CLEAN::RESUMING")

        # Defensive: stale current_colony outside the configured range
        if work.current_colony is not None and not (work.min_len <= work.current_colony <= work.max_len):
            self.logger.warn(
                f"SequentialBruteForceService::execute::STALE_CURRENT_COLONY::{work.current_colony}::RESET"
            )
            work.current_colony = None
            work.current_colony_index = -1

        # Authoritative recompute of tried combinations on resume
        if work.status in (WorkStatus.PAUSED, WorkStatus.RUNNING):
            work.total_combinations_tried = self._computeTriedCount(work)

        # EVENT: WORK_STARTED
        work.status = WorkStatus.RUNNING
        self._persist(work)
        self.logger.info("SequentialBruteForceService::execute::WORK_STARTED")

        try:
            for length in range(work.min_len, work.max_len + 1):
                # Skip completed colonies
                if length in work.completed_colonies:
                    self.logger.info(f"SequentialBruteForceService::execute::SKIP_COLONY::{length}")
                    if work.current_colony == length:
                        work.current_colony = None
                        work.current_colony_index = -1
                    continue

                total_length = PasswordCombinationGenerator.countByLength(self.charset, length)

                start_index = 0
                if length == work.current_colony and work.current_colony_index >= 0:
                    start_index = work.current_colony_index + 1

                # Colony exhausted but never marked completed (e.g. crash before COLONY_COMPLETED)
                if start_index >= total_length:
                    self.logger.info(
                        f"SequentialBruteForceService::execute::COLONY_ALREADY_EXHAUSTED::{length}"
                    )
                    self._markColonyCompleted(length, work)
                    continue

                # EVENT: COLONY_STARTED
                work.current_colony = length
                work.current_colony_index = start_index - 1
                self._persist(work)
                self.logger.info(
                    f"SequentialBruteForceService::execute::COLONY_STARTED::LEN::{length}::FROM_INDEX::{start_index}"
                )

                if self._run_colony(length, start_index, work):
                    # EVENT: PASSWORD_FOUND
                    work.status = WorkStatus.FOUND
                    work.password_found = True
                    work.completed_at = datetime.now().isoformat()
                    self._persist(work)
                    self.logger.info("SequentialBruteForceService::execute::PASSWORD_FOUND")
                    return True

                # EVENT: COLONY_COMPLETED
                self._markColonyCompleted(length, work)
        except KeyboardInterrupt:
            self.logger.warn("SequentialBruteForceService::execute::STOP_PROCESS_BY_USER")
            # EVENT: WORK_PAUSED
            work.status = WorkStatus.PAUSED
            self._persist(work)
            self.logger.info("SequentialBruteForceService::execute::WORK_PAUSED")
            return False
        except TermiteCheckError as e:
            self.logger.error(f"SequentialBruteForceService::execute::TERMITE_CHECK_ERROR::INDEX::{e.index}")
            # EVENT: WORK_PAUSED — keep last valid checkpoint, do not advance progress
            work.status = WorkStatus.PAUSED
            self._persist(work)
            self.logger.info("SequentialBruteForceService::execute::WORK_PAUSED")
            return False
        except (FileNotFoundError, PermissionError) as e:
            self.logger.error(f"SequentialBruteForceService::execute::HARD_ERROR::{e}")
            # EVENT: WORK_FAILED — unrecoverable infrastructure error
            work.status = WorkStatus.FAILED
            work.completed_at = datetime.now().isoformat()
            self._persist(work)
            self.logger.info("SequentialBruteForceService::execute::WORK_FAILED")
            return False

        # EVENT: WORK_COMPLETED
        work.status = WorkStatus.COMPLETED
        work.completed_at = datetime.now().isoformat()
        self._persist(work)
        self.logger.info(f"SequentialBruteForceService::execute::WORK_COMPLETED::FILE::{self.rar_path}")
        self.logger.info(f"SequentialBruteForceService::execute::DONT_CRACK_PASSWORD::FILE::{self.rar_path}")
        return False

    def _validate_inputs(self):
        if not os.path.isfile(self.rar_path):
            raise FileNotFoundError(f"RAR file not found: {self.rar_path}")
        if not os.path.isfile(self.unrar_path):
            raise FileNotFoundError(f"UnRAR executable not found: {self.unrar_path}")

    def _computeTriedCount(self, work) -> int:
        tried = sum(
            PasswordCombinationGenerator.countByLength(self.charset, length)
            for length in work.completed_colonies
        )
        if work.current_colony is not None and work.current_colony_index >= 0:
            tried += work.current_colony_index + 1
        return tried

    def _persist(self, work):
        work.updated_at = datetime.now().isoformat()
        self.work_repository.save(work)

    def _run_colony(self, length, start_index, work):
        self.logger.info(f"SequentialBruteForceService::_run_colony::SPAWN_COLONY::LEN::{length}")
        print(f"\n>>> SPAWNING COLONY :: LENGTH {length} :: FROM INDEX {start_index}")
        colony_path = TermiteService.spawnColony(
            self.temp_path, self.charset, length, self.logger
        )
        total = PasswordCombinationGenerator.countByLength(self.charset, length)

        tracker = BeautifulPrinter(
            label=f"TERMITES-L{length}",
            total=total,
            inline=True,
            update_every=100,
            show_current=True,
            show_speed=True,
            show_bar=False,
            header=None,
            footer=False,
        )
        tracker.start()
        tracker.current = start_index

        # Deterministic index-based iteration (NOT file positions).
        generator = PasswordCombinationGenerator.generatorForLength(self.charset, length)
        for _ in range(start_index):
            next(generator)

        for index in range(start_index, total):
            file_path = os.path.join(colony_path, f"{index}.txt")
            password = TermiteService.readTermite(file_path)
            if password is None:
                # Defensive fallback if the physical termite is missing
                password = next(generator)
            else:
                next(generator)

            tracker.update(extra_info=f"idx::{index}", current=index + 1)

            result = WinrarService.tryPassword(self.rar_path, self.unrar_path, password)

            if result == PasswordTestResult.CORRECT:
                TermiteService.survive(file_path, self.output_path)
                elapsed = tracker.elapsed
                tracker.newline()
                self.logger.info(
                    f"SequentialBruteForceService::_run_colony::TERMITE_WINNER::{index}.txt::TIME::{elapsed:.1f}s"
                )
                print("\n\nPassword found.")
                self._extract_and_log(password)
                return True
            elif result == PasswordTestResult.INCORRECT:
                TermiteService.kill(file_path)
                # EVENT: TERMITE_PROCESSED
                work.current_colony_index = index
                work.total_combinations_tried += 1
                processed_since_start = index - start_index + 1
                if work.flush_interval > 0 and processed_since_start % work.flush_interval == 0:
                    self._persist(work)
            elif result == PasswordTestResult.ERROR:
                self.logger.error(
                    f"SequentialBruteForceService::_run_colony::TERMITE_CHECK_ERROR::INDEX::{index}"
                )
                raise TermiteCheckError(index)

        tracker.newline()
        self.logger.info(f"SequentialBruteForceService::_run_colony::COLONY_DEAD::LEN::{length}")
        return False

    def _extract_and_log(self, password):
        out_dir = WinrarService.extractContent(
            self.rar_path, self.unrar_path, password, self.output_path
        )
        if not out_dir:
            self.logger.error("SequentialBruteForceService::_extract_and_log::EXTRACTION_FAILED")
            return
        self.logger.info(f"SequentialBruteForceService::_extract_and_log::EXTRACT::{out_dir}")
        for root, _, files in os.walk(out_dir):
            for fname in files:
                if ".log" in fname:
                    continue
                fpath = os.path.join(root, fname)
                size = os.path.getsize(fpath)
                self.logger.info(f"SequentialBruteForceService::_extract_and_log::FILE::{fname}::{size}_bytes")

    def _markColonyCompleted(self, length: int, work):
        self.logger.info(
            f"SequentialBruteForceService::_markColonyCompleted::TRY::LEN::{length}"
        )

        if work is None:
            raise RuntimeError("WORK_NOT_FOUND")

        # UPDATE COMPLETED COLONIES (dedup) — mutate the shared work in place
        if length not in work.completed_colonies:
            work.completed_colonies.append(length)

        # UPDATE PROGRESS
        work.current_colony = None
        work.current_colony_index = -1
        self._persist(work)

        self.logger.info(
            f"SequentialBruteForceService::_markColonyCompleted::OK::LEN::{length}"
        )
