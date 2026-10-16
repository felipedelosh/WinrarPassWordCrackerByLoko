"""
FelipedelosH
2026

Controller: orquesta el ataque de fuerza bruta sobre un archivo RAR.
"""
import os
import sys
import time
import itertools
from datetime import datetime

from src.controllers.ConfigController import Config
from src.controllers.FolderController import FolderController
from src.controllers.LoggerController import Logger
from src.services.PasswordCombinationGenerator import PasswordCombinationGenerator
from src.services.BeautifulPrinter import BeautifulPrinter
from src.services.WinrarService import WinrarService
from src.services.TermiteService import TermiteService


class Controller:
    """
    This script needs you install winrar: https://winrar.es/descargas
    """
    UNRAR = "UnRAR.exe" # INSTALL :)
    def __init__(self, path):
        self.path = path
        self.output_path = os.path.join(self.path, "OUTPUT")
        self.currentDate = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.config = Config()
        
        self.logger = Logger(self.config.getConfig("GEN_CONFIG_DISPLAY_LOGS"))
        self.logger.info(f"Controller::__init__::START_AT::{self.currentDate}")
        self.CHARSET_FILE = self.config.getConfig("GEN_CONFIG_CHARACTERS_ARR_INPUT_FILE")
        self.MIN_LEN = self.config.getConfig("GEN_CONFIG_LEN_MIN_SIZE_CHAR_SELECT_TO_CRACK")
        self.MAX_LEN = self.config.getConfig("GEN_CONFIG_LEN_MAX_SIZE_CHAR_SELECT_TO_CRACK")
        self.RAR_FILE = self.config.getConfig("RAR_FILE_TO_CRACK")
        self.rar_path = os.path.join(self.path, self.RAR_FILE)
        self.unrar_path = os.path.join(self.path, self.UNRAR)
        self.charset = self.loadCharset()
        FolderController.createInitalFolders(self.path, self.logger)
        

    # ---------- Carga de charset ----------
    def loadCharset(self) -> str:
        """Lee characters.txt desde self.path y devuelve el charset limpio."""
        charset_path = os.path.join(self.path, self.CHARSET_FILE)

        if not os.path.exists(charset_path):
            print(f"❌ No se encontró {self.CHARSET_FILE} en la carpeta del proyecto.")
            sys.exit(1)

        with open(charset_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Quitar separadores: comas, espacios, saltos de línea, tabs
        charset = ''.join(c for c in content if c not in ', \n\r\t')

        # Quitar duplicados preservando el orden
        charset = ''.join(dict.fromkeys(charset))

        if not charset:
            print(f"❌ {self.CHARSET_FILE} está vacío o no contiene caracteres válidos.")
            sys.exit(1)

        return charset


    def bruteForce(self):
        if not os.path.exists(self.rar_path):
            self.logger.error(f"Controller::bruteForce::ERR_FILE_INPUT::{self.RAR_FILE}::DONT_EXITST_PATH")
            sys.exit(1)
        if not os.path.exists(self.unrar_path):
            self.logger.error(f"Controller::bruteForce::ERR_FILE_INPUT::{self.RAR_FILE}::DONT_EXITST_FILE")
            sys.exit(1)

        total = PasswordCombinationGenerator.countTotal(self.charset, self.MIN_LEN, self.MAX_LEN)
        self.logger.info("Controller::bruteForce::TRY")
        self.logger.info(f"Controller::bruteForce::CHARS::{self.CHARSET_FILE}::TOTAL::{len(self.charset)}")
        self.logger.info(f"Controller::bruteForce::CHARS::{self.charset}")
        self.logger.info(f"Controller::bruteForce::CHARS::TOTAL_COMBINATOR::{total:,}")
        self.logger.info(f"Controller::bruteForce::LEN_FROM::{self.MIN_LEN}::LEN_TO::{self.MAX_LEN}")

        print("\n=========TERMITES INIT=========")
        print(f"PRESS: (Ctrl+C) TO STOP\n")

        temp_path = os.path.join(self.path, "TEMP")
        try:
            for length in range(self.MIN_LEN, self.MAX_LEN + 1):
                self.logger.info(f"Controller::bruteForce::SPAWN_COLONY::LEN::{length}")
                print(f"\n>>> SPAWNING COLONY :: LENGTH {length}")

                colony_path = TermiteService.spawnColony(temp_path, self.charset, length, self.logger)
                files = TermiteService.listColony(colony_path)
                total_by_length = len(files)

                tracker = BeautifulPrinter(
                    label=f"TERMITES-L{length}",
                    total=total_by_length,
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
                            f"Controller::bruteForce::TERMITE_WINNER::{filename}::"
                            f"PASSWORD::{password}::TIME::{elapsed:.1f}s"
                        )
                        print(f"\n\n🎉 ¡PASSWORD!: '{password}'")
                        self.extractAndPrint(password)
                        return

                    TermiteService.kill(file_path)

                tracker.newline()
                self.logger.info(f"Controller::bruteForce::COLONY_DEAD::LEN::{length}")
        except KeyboardInterrupt:
            self.logger.warn("Controller::bruteForce::STOP_PROCESS_BY_USER")
            return

        self.logger.info(f"Controller::bruteForce::DONT_CRACK_PASSWORD::FILE::{self.RAR_FILE}")

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
