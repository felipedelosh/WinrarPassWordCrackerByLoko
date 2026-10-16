"""
FelipedelosH
2026

Servicio: operaciones sobre un archivo RAR.
- Probar contraseña
- Extraer contenido
"""
import os
import subprocess


class WinrarService:

    @staticmethod
    def tryPassword(rar_path: str, unrar_path: str, password: str, timeout: int = 10) -> bool:
        """Devuelve True si la contraseña es correcta."""
        try:
            result = subprocess.run(
                [unrar_path, 't', '-p' + password, rar_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout
            )
            return result.returncode == 0
        except Exception:
            return False

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
