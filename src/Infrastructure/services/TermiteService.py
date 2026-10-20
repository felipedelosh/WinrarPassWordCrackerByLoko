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
    def spawnColony(temp_path: str, charset: str, length: int, logger=None, start_index: int = 0) -> str:
        """
        Crea TEMP/TERMITES-L{length}/ y dentro un .txt por cada combinación.
        Si start_index > 0, solo genera las termitas desde start_index en adelante,
        conservando los nombres de índice absoluto (start_index.txt, start_index+1.txt, ...).
        Las termitas con índice < start_index (ya procesadas) se limpian de forma segura.
        Las termitas pendientes válidas que ya existen se reutilizan.
        Retorna la ruta de la carpeta creada.
        """
        if start_index < 0:
            if logger:
                logger.error(f"TermiteService::spawnColony::INVALID_START_INDEX::{start_index}")
            raise ValueError(f"start_index must be non-negative, got {start_index}")

        colony_path = os.path.join(temp_path, f"TERMITES-L{length}")
        os.makedirs(colony_path, exist_ok=True)

        total = len(charset) ** length

        # Clean up already-processed termites (index < start_index) safely.
        TermiteService._cleanupProcessedTermites(colony_path, start_index, logger)

        # Nothing left to generate: colony already exhausted up to total.
        if start_index >= total:
            if logger:
                logger.info(
                    f"TermiteService::spawnColony::LEN::{length}::START_INDEX::{start_index}::TOTAL::{total}::NOTHING_TO_GENERATE"
                )
            return colony_path

        # Generate only from start_index onwards. itertools.islice advances the
        # underlying product iterator without materializing skipped combinations.
        generated = 0
        reused = 0
        combinations = itertools.product(charset, repeat=length)
        for index, combo in enumerate(
            itertools.islice(combinations, start_index, total),
            start=start_index,
        ):
            password = ''.join(combo)
            file_path = os.path.join(colony_path, f"{index}.txt")
            if os.path.exists(file_path):
                existing = TermiteService.readTermite(file_path)
                if existing == password:
                    reused += 1
                    continue
                if logger:
                    logger.warn(
                        f"TermiteService::spawnColony::STALE_TERMITE::{index}.txt::REGENERATING"
                    )
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(password)
            except Exception as e:
                if logger:
                    logger.error(f"TermiteService::spawnColony::ERR::{file_path}::{str(e)}")
            generated += 1

        if logger:
            logger.info(
                f"TermiteService::spawnColony::LEN::{length}::FROM_INDEX::{start_index}::GENERATED::{generated}::REUSED::{reused}"
            )

        return colony_path

    @staticmethod
    def _cleanupProcessedTermites(colony_path: str, start_index: int, logger=None):
        """Remove termite files with absolute index < start_index (already processed)."""
        if start_index <= 0:
            return
        try:
            entries = os.listdir(colony_path)
        except Exception as e:
            if logger:
                logger.warn(f"TermiteService::_cleanupProcessedTermites::ERR::{colony_path}::{str(e)}")
            return
        for entry in entries:
            if not entry.endswith('.txt'):
                continue
            try:
                index = int(entry.split('.')[0])
            except ValueError:
                continue
            if index < start_index:
                file_path = os.path.join(colony_path, entry)
                try:
                    os.remove(file_path)
                except Exception as e:
                    if logger:
                        logger.warn(f"TermiteService::_cleanupProcessedTermites::REMOVE_ERR::{file_path}::{str(e)}")

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
