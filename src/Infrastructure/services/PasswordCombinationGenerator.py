"""
FelipedelosH
2026

Servicio: genera las combinaciones de contraseñas agrupadas por longitud.
- Retorna un iterador por cada longitud (chunk).
- Cada chunk sabe su total de combinaciones y su iterador de passwords.
"""
import itertools


class PasswordCombinationGenerator:
    @staticmethod
    def generateByLength(charset: str, min_len: int, max_len: int):
        """
        Generador de chunks. Cada yield entrega:
            (length, total_this_length, iterator_of_passwords)

        Ejemplo:
            for length, total, gen in BruteForceGenerator.generateByLength("abc", 1, 3):
                # chunk length=1 → 3 combinaciones
                # chunk length=2 → 9 combinaciones
                # chunk length=3 → 27 combinaciones
        """
        for length in range(min_len, max_len + 1):
            total = len(charset) ** length
            yield length, total, PasswordCombinationGenerator.generatorForLength(charset, length)

    @staticmethod
    def generatorForLength(charset: str, length: int):
        """Genera todas las combinaciones para UNA longitud específica."""
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)

    @staticmethod
    def countByLength(charset: str, length: int) -> int:
        return len(charset) ** length

    @staticmethod
    def countTotal(charset: str, min_len: int, max_len: int) -> int:
        return sum(len(charset) ** n for n in range(min_len, max_len + 1))
