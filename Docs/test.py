"""
FelipedelosH
2026

Enter a winrar file '.rar' and usages characters.txt to generate a brute force attack.
"""
import os
import subprocess
import itertools
import string
import sys
import time

# ============ CONFIG ============
RAR_FILE = "Docs/rar_examples/abc.rar"
UNRAR = "UnRAR.exe"

# Charset a usar (personalízalo)
CHARSET = string.ascii_lowercase  # a-z
# CHARSET = string.ascii_lowercase + string.digits          # a-z 0-9
# CHARSET = string.ascii_letters + string.digits            # a-z A-Z 0-9
# CHARSET = string.ascii_letters + string.digits + "._-@:/" # + símbolos

MIN_LEN = 1
MAX_LEN = 4   # 👈 cuidado: cada carácter más multiplica el tiempo
# =======================================


def get_paths():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, RAR_FILE), os.path.join(base, UNRAR)


def try_password(rar_path, unrar_path, password):
    """Devuelve True si la contraseña es correcta."""
    try:
        result = subprocess.run(
            [unrar_path, 't', '-p' + password, rar_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def brute_force(charset, min_len, max_len):
    """Generador que produce todas las combinaciones posibles."""
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)


def extract_content(rar_path, unrar_path, password):
    """Extrae el RAR a una carpeta y muestra el contenido."""
    out_dir = os.path.join(os.path.dirname(rar_path), "extraido")
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n📦 Extrayendo con contraseña '{password}'...")
    result = subprocess.run(
        [unrar_path, 'x', '-p' + password, '-o+', rar_path, out_dir + os.sep],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print("⚠️ No se pudo extraer:", result.stderr)
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


def main():
    rar_path, unrar_path = get_paths()

    if not os.path.exists(rar_path):
        print(f"❌ No se encontró {RAR_FILE} en la carpeta.")
        sys.exit(1)
    if not os.path.exists(unrar_path):
        print(f"❌ No se encontró {UNRAR} en la carpeta.")
        print("   Cópialo desde C:\\Program Files\\WinRAR\\UnRAR.exe")
        sys.exit(1)

    total = sum(len(CHARSET) ** n for n in range(MIN_LEN, MAX_LEN + 1))
    print(f"🔍 Iniciando fuerza bruta")
    print(f"   Charset: {CHARSET}")
    print(f"   Longitud: {MIN_LEN} a {MAX_LEN}")
    print(f"   Combinaciones totales: {total:,}")
    print(f"   (Ctrl+C para detener)\n")

    start = time.time()
    count = 0

    try:
        for password in brute_force(CHARSET, MIN_LEN, MAX_LEN):
            count += 1
            if count % 100 == 0 or count == 1:
                elapsed = time.time() - start
                speed = count / elapsed if elapsed > 0 else 0
                print(f"   [{count}/{total}] probando: {password}  ({speed:.1f}/s)", end='\r')

            if try_password(rar_path, unrar_path, password):
                elapsed = time.time() - start
                print(f"\n\n🎉 ¡CONTRASEÑA ENCONTRADA!: '{password}'")
                print(f"   Probadas {count} combinaciones en {elapsed:.1f} segundos.\n")
                extract_content(rar_path, unrar_path, password)
                return

    except KeyboardInterrupt:
        print("\n\n⏹️ Detenido por el usuario.")
        return

    print("\n\n❌ No se encontró la contraseña en el rango probado.")


if __name__ == "__main__":
    main()
