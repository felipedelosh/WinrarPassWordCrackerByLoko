"""
FelipedelosH
2026

Servicio: operaciones sobre un archivo RAR.
- Probar contraseña
- Extraer contenido
"""
import os
import hashlib
import subprocess
from src.Models.Enums.PasswordTestResult import PasswordTestResult


class WinrarService:

    @staticmethod
    def tryPassword(rar_path: str, unrar_path: str, password: str, timeout: int = 10) -> PasswordTestResult:
        """
        Comprueba una contraseña contra el RAR.

        Retorna:
            - CORRECT  si la contraseña es correcta (returncode 0).
            - INCORRECT si la comprobación finalizó y la contraseña es incorrecta (returncode != 0).
            - ERROR    si ocurrió un fallo técnico transitorio (timeout u otro error de subprocess);
                        la comprobación NO finalizó y el progreso no debe avanzar.

        Los errores duros (FileNotFoundError, PermissionError) se relanzan: indican que el
        binario o el RAR desaparecieron y no se recuperan reintentando.
        """
        try:
            result = subprocess.run(
                [unrar_path, 't', '-p' + password, rar_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout
            )
            if result.returncode == 0:
                return PasswordTestResult.CORRECT
            return PasswordTestResult.INCORRECT
        except FileNotFoundError:
            raise
        except PermissionError:
            raise
        except Exception:
            return PasswordTestResult.ERROR

    @staticmethod
    def computeSha256(path: str) -> str:
        """
        Calcula el SHA-256 del contenido de un archivo (lectura por chunks).
        Relanza FileNotFoundError si el archivo no existe.
        """
        hasher = hashlib.sha256()
        with open(path, "rb") as file:
            for chunk in iter(lambda: file.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def extractContent(rar_path: str, unrar_path: str, password: str, out_dir: str) -> str:
        """Extrae el RAR a la carpeta indicada y devuelve esa ruta."""
        os.makedirs(out_dir, exist_ok=True)

        result = subprocess.run(
            [unrar_path, 'x', '-p' + password, '-o+', rar_path, out_dir + os.sep],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print("⚠️ No se pudo extraer:", result.stderr)
            return None

        return out_dir
