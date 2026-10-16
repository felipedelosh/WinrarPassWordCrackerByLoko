"""
FelipedelosH
2026

This is the main controller of WinrarPassWordCrackerByLoko
"""
import os
import subprocess


class Controller:
    """Encapsula todas las operaciones sobre un archivo RAR."""

    def __init__(self, unrar_path):
        self.unrar_path = unrar_path

    # ---------- Probar contraseña ----------
    def try_password(self, rar_path, password, timeout=10):
        """Devuelve True si la contraseña es correcta."""
        try:
            result = subprocess.run(
                [self.unrar_path, 't', '-p' + password, rar_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout
            )
            return result.returncode == 0
        except Exception:
            return False

    # ---------- Extraer ----------
    def extract_content(self, rar_path, password, out_dir_name="extraido"):
        """Extrae el RAR a una carpeta y devuelve la ruta de esa carpeta."""
        out_dir = os.path.join(os.path.dirname(rar_path), out_dir_name)
        os.makedirs(out_dir, exist_ok=True)

        result = subprocess.run(
            [self.unrar_path, 'x', '-p' + password, '-o+', rar_path, out_dir + os.sep],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"No se pudo extraer: {result.stderr}")

        return out_dir

    # ---------- Listar archivos extraídos ----------
    def list_extracted_files(self, folder):
        """Devuelve la lista de rutas absolutas de archivos dentro de folder."""
        files = []
        for root, _, filenames in os.walk(folder):
            for fname in filenames:
                files.append(os.path.join(root, fname))
        return files

    # ---------- Guardar resultados ----------
    def save_results(self, password, out_dir, save_path=None):
        """Guarda la contraseña y el listado de archivos extraídos en un .txt.
        Devuelve la ruta del archivo generado."""
        if save_path is None:
            save_path = os.path.join(out_dir, "resultado.txt")

        files = self.list_extracted_files(out_dir)

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(f"Contraseña encontrada: {password}\n")
            f.write(f"Carpeta de extracción: {out_dir}\n")
            f.write(f"Total archivos extraídos: {len(files)}\n")
            f.write("-" * 40 + "\n")
            for path in files:
                rel = os.path.relpath(path, out_dir)
                f.write(f"  - {rel}\n")

        return save_path
