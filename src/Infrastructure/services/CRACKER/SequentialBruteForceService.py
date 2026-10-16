"""
FelipedelosH
2026
"""
# src\Infrastructure\services\CRACKER\SequentialBruteForceService.py
import os
from src.Application.services.CRACKER.IBruteForceService import IBruteForceService
from src.Infrastructure.services.PasswordCombinationGenerator import PasswordCombinationGenerator
from src.Infrastructure.services.TermiteService import TermiteService
from src.Infrastructure.services.WinrarService import WinrarService
from src.Infrastructure.services.BeautifulPrinter import BeautifulPrinter


class SequentialBruteForceService(IBruteForceService):
    def __init__(self, rar_path, unrar_path, charset, min_len, max_len, temp_path, output_path, logger):
        self.rar_path = rar_path
        self.unrar_path = unrar_path
        self.charset = charset
        self.min_len = min_len
        self.max_len = max_len
        self.temp_path = temp_path
        self.output_path = output_path
        self.logger = logger


    def execute(self):
        """Execute the existing sequential colony workflow."""
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

        try:
            for length in range(self.min_len, self.max_len + 1):
                if self._run_colony(length):
                    return True
        except KeyboardInterrupt:
            self.logger.warn("SequentialBruteForceService::execute::STOP_PROCESS_BY_USER")
            return False

        self.logger.info(f"SequentialBruteForceService::execute::DONT_CRACK_PASSWORD::FILE::{self.rar_path}")
        return False

    def _validate_inputs(self):
        if not os.path.isfile(self.rar_path):
            raise FileNotFoundError(f"RAR file not found: {self.rar_path}")
        if not os.path.isfile(self.unrar_path):
            raise FileNotFoundError(f"UnRAR executable not found: {self.unrar_path}")

    def _run_colony(self, length):
        self.logger.info(f"SequentialBruteForceService::_run_colony::SPAWN_COLONY::LEN::{length}")
        print(f"\n>>> SPAWNING COLONY :: LENGTH {length}")
        colony_path = TermiteService.spawnColony(
            self.temp_path, self.charset, length, self.logger
        )
        files = TermiteService.listColony(colony_path)
        tracker = BeautifulPrinter(
            label=f"TERMITES-L{length}",
            total=len(files),
            inline=True,
            update_every=100,
            show_current=True,
            show_speed=True,
            show_bar=False,
            header=None,
            footer=False,
        )
        tracker.start()
        for filename in files:
            file_path = os.path.join(colony_path, filename)
            password = TermiteService.readTermite(file_path)
            tracker.update(extra_info=f"trying: {password}")
            if WinrarService.tryPassword(self.rar_path, self.unrar_path, password):
                TermiteService.survive(file_path, self.output_path)
                elapsed = tracker.elapsed
                tracker.newline()
                self.logger.info(
                    f"SequentialBruteForceService::_run_colony::TERMITE_WINNER::{filename}::TIME::{elapsed:.1f}s"
                )
                print("\n\nPassword found.")
                self._extract_and_log(password)
                return True
            TermiteService.kill(file_path)
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
