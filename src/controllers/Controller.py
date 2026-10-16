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
