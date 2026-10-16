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
from src.services.WinrarService import WinrarService


class Controller:
    UNRAR        = "UnRAR.exe"

    MIN_LEN = 1
    MAX_LEN = 4   # 👈 cuidado: cada carácter más multiplica el tiempo
    def __init__(self, path):
        self.path = path
        self.output_path = os.path.join(self.path, "OUTPUT")
        self.currentDate = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.config = Config()
        
        self.logger = Logger(self.config.getConfig("GEN_CONFIG_DISPLAY_LOGS"))
        self.logger.info(f"Controller::__init__::START_AT::{self.currentDate}")
        self.CHARSET_FILE = self.config.getConfig("GEN_CONFIG_CHARACTERS_ARR_INPUT_FILE")

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

    # ---------- Orquestador ----------
    def bruteForce(self):
        # Validar rutas
        if not os.path.exists(self.rar_path):
            print(f"❌ No se encontró {self.RAR_FILE} en la carpeta.")
            sys.exit(1)
        if not os.path.exists(self.unrar_path):
            print(f"❌ No se encontró {self.UNRAR} en la carpeta.")
            print("   Cópialo desde C:\\Program Files\\WinRAR\\UnRAR.exe")
            sys.exit(1)

        total = self.countCombinations(self.charset, self.MIN_LEN, self.MAX_LEN)
        print(f"🔍 Iniciando fuerza bruta")
        print(f"   Charset cargado desde {self.CHARSET_FILE}")
        print(f"   Caracteres: {self.charset}")
        print(f"   Longitud: {self.MIN_LEN} a {self.MAX_LEN}")
        print(f"   Combinaciones totales: {total:,}")
        print(f"   (Ctrl+C para detener)\n")

        start = time.time()
        count = 0

        try:
            for password in self.bruteForceGenerator(self.charset, self.MIN_LEN, self.MAX_LEN):
                count += 1
                if count % 100 == 0 or count == 1:
                    elapsed = time.time() - start
                    speed = count / elapsed if elapsed > 0 else 0
                    print(f"   [{count}/{total}] probando: {password}  ({speed:.1f}/s)", end='\r')

                if WinrarService.tryPassword(self.rar_path, self.unrar_path, password):
                    elapsed = time.time() - start
                    print(f"\n\n🎉 ¡CONTRASEÑA ENCONTRADA!: '{password}'")
                    print(f"   Probadas {count} combinaciones en {elapsed:.1f} segundos.\n")
                    self.extractAndPrint(password)
                    return

        except KeyboardInterrupt:
            print("\n\n⏹️ Detenido por el usuario.")
            return

        print("\n\n❌ No se encontró la contraseña en el rango probado.")

    # ---------- Helpers internos ----------
    def bruteForceGenerator(self, charset, min_len, max_len):
        """Generador que produce todas las combinaciones posibles."""
        for length in range(min_len, max_len + 1):
            for combo in itertools.product(charset, repeat=length):
                yield ''.join(combo)

    def countCombinations(self, charset, min_len, max_len) -> int:
        return sum(len(charset) ** n for n in range(min_len, max_len + 1))

    def extractAndPrint(self, password):
        out_dir = WinrarService.extractContent(self.rar_path, self.unrar_path, password, self.output_path)
        if not out_dir:
            return

        print(f"✅ Extraído en: {out_dir}\n")
        print("📄 Contenido de los archivos de texto encontrados:\n")

        for root, _, files in os.walk(out_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                print(f"--- {fname} ---")
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        print(f.read())
                except Exception as e:
                    print(f"(No es texto legible: {e})")
                print()

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
