"""
FelipedelosH
2026

Main application controller responsible for orchestrating
brute-force strategies, initializing required resources,
managing dependencies, and saving execution logs.
"""
import os
from datetime import datetime

from src.CORE.Config import Config
from src.CORE.FolderController import FolderController
from src.Infrastructure.services.WinrarService import WinrarService
from src.Models.Enums.Attack import Attack
from src.Models.Entities.WorkState import WorkState
from src.Models.Enums.WorkStatus import WorkStatus

class Controller:
    def __init__(self, path: str, config: Config, dependencies: dict):
        self.path = path
        self.dependencies = dependencies
        self.output_path = os.path.join(self.path, "OUTPUT")
        self.currentDate = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.config = config
        self.logger = dependencies["logger"]
        self.logger.info(f"Controller::__init__::START_AT::{self.currentDate}")
        self.CHARSET_FILE = self.config.getConfig("GEN_CONFIG_CHARACTERS_ARR_INPUT_FILE")
        self.MIN_LEN = self.config.getConfig("GEN_CONFIG_LEN_MIN_SIZE_CHAR_SELECT_TO_CRACK")
        self.MAX_LEN = self.config.getConfig("GEN_CONFIG_LEN_MAX_SIZE_CHAR_SELECT_TO_CRACK")
        self.RAR_FILE = self.config.getConfig("RAR_FILE_TO_CRACK")
        self.rar_path = os.path.join(self.path, self.RAR_FILE)
        self.unrar_path = os.path.join(self.path, self.config.getConfig("UNRAR_SOFTWARE_FILE_PATH"))
        FolderController.createInitalFolders(self.path, self.logger)

        # Vars
        self.work_state = None

        self.loadPreviousWork()


    def loadPreviousWork(self):
        self.logger.info("Controller::loadPreviousWork::TRY")

        repository = self.dependencies["work_repository"]

        # LOAD PREVIOUS WORK
        if repository.exists():
            try:
                self.work_state = repository.load()

                self.logger.info(
                    f"Controller::loadPreviousWork::FOUND::"
                    f"STATUS::{self.work_state.status}"
                )

                self.logger.info(
                    f"Controller::loadPreviousWork::"
                    f"CURRENT_COLONY::{self.work_state.current_colony}::"
                    f"CURRENT_INDEX::{self.work_state.current_colony_index}"
                )

                return self.work_state

            except (OSError, ValueError, KeyError, TypeError) as e:
                self.logger.error(
                    f"Controller::loadPreviousWork::ERROR::{e}"
                )
                raise

        # CREATE NEW WORK
        self.logger.info("Controller::loadPreviousWork::NOT_FOUND")

        charset_path = os.path.join(self.path, self.CHARSET_FILE)

        with open(charset_path, "r", encoding="utf-8") as file:
            content = file.read()

        charset = "".join(c for c in content if c not in ", \n\r\t")
        charset = "".join(dict.fromkeys(charset))

        if not charset:
            raise ValueError("The charset cannot be empty.")

        min_len = int(self.MIN_LEN)
        max_len = int(self.MAX_LEN)

        if min_len < 1 or max_len < min_len:
            raise ValueError("Invalid password length range.")

        total_combinations = sum(
            len(charset) ** length
            for length in range(min_len, max_len + 1)
        )

        rar_file = os.path.relpath(self.rar_path, self.path)
        rar_size_bytes = (
            os.path.getsize(self.rar_path)
            if os.path.isfile(self.rar_path)
            else 0
        )

        self.work_state = WorkState(
            rar_file=rar_file,
            rar_size_bytes=rar_size_bytes,
            charset=charset,
            min_len=min_len,
            max_len=max_len,
            attack_mode=self.config.getConfig("GEN_CONFIG_ATTACK_MODE"),
            status=WorkStatus.NEW,
            password_found=False,
            total_colonies=max_len - min_len + 1,
            total_combinations=total_combinations,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        repository.save(self.work_state)

        self.logger.info(
            "Controller::loadPreviousWork::CREATE::NEW"
        )

        return self.work_state


    def bruteForce(self):
        _mode = self.config.getConfig("GEN_CONFIG_ATTACK_MODE")
        self.logger.info(f"Controller::bruteForce::TRY::{_mode}")
        if _mode == str(Attack.RANDOM):
            pass

        if _mode == str(Attack.SEQUENTIAL):
            return self.dependencies["sequential_brute_force"].execute()
        
        return None

    def extractAndPrint(self, password):
        self.logger.info(f"Controller::extractAndPrint::TRY::{password}")
        out_dir = WinrarService.extractContent(self.rar_path, self.unrar_path, password, self.output_path)
        if not out_dir:
            self.logger.error(f"Controller::extractAndPrint::ERR_PATH::{out_dir}::NOT_FOUND")
            return

        self.logger.info(f"Controller::extractAndPrint::EXTRACT::{out_dir}")
        for root, _, files in os.walk(out_dir):
            for fname in files:
                if ".log" in fname:
                    continue
                fpath = os.path.join(root, fname)
                size = os.path.getsize(fpath)
                self.logger.info(f"Controller::extractAndPrint::FILE::{fname}::{size}_bytes")

    def saveLogs(self):
        try:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
            filename = f"logs_{timestamp}.log"
            full_path = os.path.join(self.output_path, filename)

            with open(full_path, "w", encoding="UTF-8") as f:
                f.write(self.logger.log)
            print(f"LOGs: {full_path}")
        except Exception as e:
            print(f"ERROR FATAL IN saveLogs: {e}")
