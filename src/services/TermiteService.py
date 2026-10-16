"""
FelipedelosH
2026

Servicio: colonia de termitas.
Cada termita es un .txt dentro de TEMP/TERMITES-L{length}/
El nombre del archivo es su índice (0.txt, 1.txt, ...)
El contenido del archivo es la password a probar.
"""
import os
import itertools


class TermiteService:
    @staticmethod
    def spawnColony(temp_path: str, charset: str, length: int, logger=None) -> str:
        """
        Crea TEMP/TERMITES-L{length}/ y dentro un .txt por cada combinación.
        Retorna la ruta de la carpeta creada.
        """
        colony_path = os.path.join(temp_path, f"TERMITES-L{length}")
        os.makedirs(colony_path, exist_ok=True)

        index = 0
        for combo in itertools.product(charset, repeat=length):
            password = ''.join(combo)
            file_path = os.path.join(colony_path, f"{index}.txt")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(password)
            except Exception as e:
                if logger:
                    logger.error(f"TermiteService::spawnColony::ERR::{file_path}::{str(e)}")
            index += 1

        if logger:
            logger.info(f"TermiteService::spawnColony::LEN::{length}::TOTAL::{index}")

        return colony_path

    @staticmethod
    def listColony(colony_path: str) -> list:
        """Lista los archivos de la colonia ordenados por índice numérico."""
        try:
            return sorted(
                os.listdir(colony_path),
                key=lambda x: int(x.split('.')[0])
            )
        except Exception:
            return []

    @staticmethod
    def readTermite(file_path: str):
        """Lee el contenido (password) de una termita."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    @staticmethod
    def kill(file_path: str):
        """La termita muere: se borra su archivo."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

    @staticmethod
    def survive(file_path: str, output_path: str):
        """La termita sobrevive: su archivo se mueve a OUTPUT."""
        try:
            filename = os.path.basename(file_path)
            dest = os.path.join(output_path, f"TERMITE_WINNER_{filename}")
            os.rename(file_path, dest)
        except Exception:
            pass
