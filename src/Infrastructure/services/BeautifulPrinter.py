"""
FelipedelosH
2026

BeautifulPrinter: muestra el progreso de una operación por consola.
Configurable: label, total, barra, porcentaje, tiempo, extras, thresholds.

Dos modos:
    - Continuo:   imprime en cada update()
    - Thresholds: solo imprime al alcanzar ciertos porcentajes (0.1, 0.5, 1.0, ...)
"""
import time


class BeautifulPrinter:

    def __init__(
        self,
        label: str,
        total: int,
        thresholds: list = None,
        bar_size: int = 40,
        show_bar: bool = True,
        show_percentage: bool = True,
        show_elapsed: bool = True,
        show_current: bool = True,
        show_eta: bool = False,
        show_speed: bool = False,
        separator: str = "|",
        header: str = None,
        footer: bool = True,
        inline: bool = False,
        update_every: int = 100,
    ):
        self.label = label
        self.total = total
        self.thresholds = thresholds if thresholds else []
        self.bar_size = bar_size
        self.show_bar = show_bar
        self.show_percentage = show_percentage
        self.show_elapsed = show_elapsed
        self.show_current = show_current
        self.show_eta = show_eta
        self.separator = separator
        self.header = header
        self.footer = footer

        self.current = 0
        self.start_time = None
        self.last_threshold_time = None
        self._threshold_index = 0
        self.show_speed = show_speed
        self.inline = inline
        self.update_every = update_every

    # ---------------------------------------------------
    # CICLO DE VIDA
    # ---------------------------------------------------
    def start(self):
        self.start_time = time.perf_counter()
        self.last_threshold_time = self.start_time
        self._threshold_index = 0
        self.current = 0

        if self.header:
            print("=" * 70)
            print(self.header)
            print(f"Total : {self.total}")
            print("=" * 70)

    def update(self, extra_info: str = "", current: int = None):
        self.current = current if current is not None else self.current + 1

        if self.total <= 0 or self.start_time is None:
            return

        ratio = self.current / self.total
        now = time.perf_counter()
        elapsed = now - self.start_time

        # ---------- MODO INLINE ----------
        if self.inline:
            if self.current % self.update_every != 0 and self.current != 1:
                return

            parts = []
            if self.show_current:
                parts.append(f"{self.current}/{self.total}")
            if extra_info:
                parts.append(extra_info)
            if self.show_speed:
                speed = self.current / elapsed if elapsed > 0 else 0
                parts.append(f"({speed:.1f}/s)")

            print(f"[{self.label}] " + "  ".join(parts), end='\r', flush=True)
            return

        # ---------- MODO THRESHOLD ----------
        # ...igual que antes...

        # ---------- MODO CONTINUO ----------
        # ...igual que antes...

    def finish(self, extra_info: str = ""):
        if self.start_time is None or not self.footer:
            return

        elapsed = time.perf_counter() - self.start_time
        print("=" * 70)
        print(
            f"[{self.label}] COMPLETED "
            f"{self.separator} {self.total}/{self.total} "
            f"{self.separator} 100.00% "
            f"{self.separator} Total: {self._fmt(elapsed)}"
            + (f" {self.separator} {extra_info}" if extra_info else "")
        )
        if self.show_bar:
            print(f"[{self._bar(100)}] 100.00%")
        print("=" * 70)

    # ---------------------------------------------------
    # HELPERS INTERNOS
    # ---------------------------------------------------
    def _bar(self, percentage):
        filled = int((percentage / 100) * self.bar_size)
        return "#" * filled + "-" * (self.bar_size - filled)

    def _fmt(self, seconds):
        if seconds < 60:
            return f"{seconds:.2f} s"
        if seconds < 3600:
            return f"{seconds / 60:.2f} min"
        return f"{seconds / 3600:.2f} h"

    def newline(self):
        """Cierra la línea inline para poder escribir el mensaje final."""
        if self.inline:
            print()

    @property
    def elapsed(self):
        """Segundos transcurridos desde start()."""
        if self.start_time is None:
            return 0
        return time.perf_counter() - self.start_time
