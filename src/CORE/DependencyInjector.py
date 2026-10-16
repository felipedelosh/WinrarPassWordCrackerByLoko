"""
FelipedelosH
2026

Centralized Dependency Injector.
"""
# src\CORE\DependencyInjector.py
import os
from src.CORE.Config import Config
from src.CORE.Logger import Logger
from src.Infrastructure.services.CRACKER.SequentialBruteForceService import (SequentialBruteForceService)
from src.Infrastructure.repositories.JsonWorkRepository import (JsonWorkRepository)


class DependencyInjector:
    @staticmethod
    def build_dependencies(path: str, config: Config) -> dict:

        # CONFIGURATION
        rar_path = config.getConfig("RAR_FILE_TO_CRACK")
        unrar_path = config.getConfig("UNRAR_SOFTWARE_FILE_PATH")

        min_len = int(config.getConfig("GEN_CONFIG_LEN_MIN_SIZE_CHAR_SELECT_TO_CRACK"))
        max_len = int(config.getConfig("GEN_CONFIG_LEN_MAX_SIZE_CHAR_SELECT_TO_CRACK"))

        temp_path = os.path.join(path, "TEMP")
        output_path = os.path.join(path, "OUTPUT")

        # WORK REPOSITORY
        work_path = os.path.join(temp_path, "work.json")

        work_repository = JsonWorkRepository(
            work_path=work_path
        )

        # CHARSET
        charset_path = os.path.join(path, "characters.txt")

        with open(charset_path, "r", encoding="utf-8") as file:
            content = file.read()

        charset = "".join(
            c for c in content if c not in ", \n\r\t"
        )

        charset = "".join(dict.fromkeys(charset))

        if not charset:
            raise ValueError("The charset cannot be empty.")

        # LOGGER
        logger = Logger(config.getConfig("GEN_CONFIG_DISPLAY_LOGS"))

        # SERVICES - CRACKERS
        sequential_brute_force = SequentialBruteForceService(
            rar_path=rar_path,
            unrar_path=unrar_path,
            charset=charset,
            min_len=min_len,
            max_len=max_len,
            temp_path=temp_path,
            output_path=output_path,
            logger=logger
        )

        return {
            "work_repository": work_repository,
            "sequential_brute_force": sequential_brute_force,
            "logger": logger
        }
