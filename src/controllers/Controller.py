"""
FelipedelosH
2026

Controller: orquesta el ataque de fuerza bruta sobre un archivo RAR.
"""
import os
import sys
import time
import string
import itertools

from src.services.WinrarService import WinrarService


class Controller:

    # ============ CONFIG ============
    RAR_FILE = os.path.join("Docs", "rar_examples", "abc.rar")
    UNRAR    = "UnRAR.exe"

    # Charset a usar (personalízalo)
    CHARSET = string.ascii_lowercase  # a-z
    # CHARSET = string.ascii_lowercase + string.digits          # a-z 0-9
    # CHARSET = string.ascii_letters + string.digits            # a-z A-Z 0-9
    # CHARSET = string.ascii_letters + string.digits + "._-@:/" # + símbolos

    MIN_LEN = 1
    MAX_LEN = 4   # 👈 cuidado: cada carácter más multiplica el tiempo
    # ================================

    def __init__(self, path):
        self.path = path
        self.rar_path = os.path.join(self.path, self.RAR_FILE)
        self.unrar_path = os.path.join(self.path, self.UNRAR)

    def bruteForce(self):
        # Validar rutas
        if not os.path.exists(self.rar_path):
            print(f"❌ No se encontró {self.RAR_FILE} en la carpeta.")
            sys.exit(1)
        if not os.path.exists(self.unrar_path):
            print(f"❌ No se encontró {self.UNRAR} en la carpeta.")
            print("   Cópialo desde C:\\Program Files\\WinRAR\\UnRAR.exe")
            sys.exit(1)

        total = self.countCombinations(self.CHARSET, self.MIN_LEN, self.MAX_LEN)
        print(f"🔍 Iniciando fuerza bruta")
        print(f"   Charset: {self.CHARSET}")
        print(f"   Longitud: {self.MIN_LEN} a {self.MAX_LEN}")
        print(f"   Combinaciones totales: {total:,}")
        print(f"   (Ctrl+C para detener)\n")

        start = time.time()
        count = 0

        try:
            for password in self.bruteForceGenerator(self.CHARSET, self.MIN_LEN, self.MAX_LEN):
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
        out_dir = WinrarService.extractContent(self.rar_path, self.unrar_path, password)
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
