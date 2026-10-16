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
        separator: str = "|",
        header: str = None,
        footer: bool = True,
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
        """
        Avanza el contador.
            - Si thresholds está definido >> solo imprime al cruzar cada umbral.
            - Si thresholds está vacío  >> imprime en cada llamada.
        extra_info: texto libre para agregar al final de la línea (ej: "Orders: 250")
        """
        self.current = current if current is not None else self.current + 1

        if self.total <= 0 or self.start_time is None:
            return

        ratio = self.current / self.total
        now = time.perf_counter()
        elapsed = now - self.start_time

        # ---- MODO THRESHOLD ----
        if self.thresholds:
            if self._threshold_index >= len(self.thresholds):
                return
            target = self.thresholds[self._threshold_index]
            if ratio < target:
                return

            interval = now - self.last_threshold_time
            print(
                f"[{self.label}] {self.current}/{self.total} "
                f"({int(target * 100)}%) "
                f"{self.separator} Intervalo: {self._fmt(interval)} "
                f"{self.separator} Total: {self._fmt(elapsed)}"
                + (f" {self.separator} {extra_info}" if extra_info else "")
            )
            self.last_threshold_time = now
            self._threshold_index += 1
            return

        # ---- MODO CONTINUO ----
        parts = []
        if self.show_current:
            parts.append(f"{self.current}/{self.total}")
        if self.show_percentage:
            parts.append(f"{ratio * 100:.2f}%")
        if self.show_eta and self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            parts.append(f"ETA: {self._fmt(eta)}")
        if self.show_elapsed:
            parts.append(f"Total: {self._fmt(elapsed)}")
        if extra_info:
            parts.append(extra_info)

        print(f"[{self.label}] " + f" {self.separator} ".join(parts))

        if self.show_bar:
            print(f"[{self._bar(ratio * 100)}] {ratio * 100:.2f}%")

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
