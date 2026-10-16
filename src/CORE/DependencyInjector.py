# CORE/DependencyInjector.py

# Services
from src.services.CRACKER.SequentialBruteForceService import SequentialBruteForceService


class DependencyInjector:
    @staticmethod
    def build_dependencies(rar_path, unrar_path, charset, min_len, max_len, temp_path, output_path, logger):

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
            "sequential_brute_force": sequential_brute_force
        }
