import math
import numpy as np

WIRE_MU = {
    '0.7mm': 7800 * math.pi * (0.35e-3) ** 2,
    '0.8mm': 7800 * math.pi * (0.40e-3) ** 2,
    '0.9mm': 7800 * math.pi * (0.45e-3) ** 2,
    '1.0mm': 7800 * math.pi * (0.50e-3) ** 2,
}


class Biriba:
    def __init__(self, name: str, L0_cm: float, L_cm: float,
                 calibre: str = None, f1_measured: float = 0.0, mu: float = None):
        self.name = name
        self.L0 = L0_cm * 1e-2
        self.L = L_cm * 1e-2
        if mu is not None:
            self.mu = mu
        elif calibre is not None:
            self.mu = WIRE_MU[calibre]
        else:
            raise ValueError("calibre or mu required")
        self.calibre = calibre or ''
        self.f1_measured = f1_measured
        self.k = self._calc_k()

    def _calc_k(self) -> float:
        T = self.mu * (2 * self.L * self.f1_measured) ** 2
        return T / (self.L0 - self.L)

    def f1_at(self, L_m: float) -> float:
        T = self.k * (self.L0 - L_m)
        if T <= 0:
            return 0.0
        return (1 / (2 * L_m)) * math.sqrt(T / self.mu)

    def freq_range(self, L_min_cm: float = None, L_max_cm: float = None):
        delta = self.L0 - self.L
        L_min = (L_min_cm * 1e-2) if L_min_cm else max(self.L - 2 * delta, self.L0 * 0.80)
        L_max = (L_max_cm * 1e-2) if L_max_cm else self.L0 * 0.995
        L_vals = np.linspace(L_min, L_max, 300)
        freqs = np.array([self.f1_at(L) for L in L_vals])
        return L_vals, freqs

    def __repr__(self):
        fmin = min(f for f in self.freq_range()[1] if f > 0)
        fmax = max(self.freq_range()[1])
        return f"Biriba('{self.name}', k={self.k:.1f} N/m, {fmin:.0f}–{fmax:.0f} Hz)"
