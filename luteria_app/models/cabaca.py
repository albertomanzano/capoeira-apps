import math

C_SOUND = 343.0  # m/s


class Cabaca:
    def __init__(self, name: str, V_ml: float, d_mm: float, f_H_measured: float = None):
        self.name = name
        self.V = V_ml * 1e-6          # m³
        self.r = (d_mm / 2) * 1e-3   # m
        self.f_H_measured = f_H_measured

    @property
    def f_H(self) -> float:
        if self.f_H_measured is not None:
            return self.f_H_measured
        return (C_SOUND / (2 * math.pi)) * math.sqrt(math.pi * self.r / (0.85 * self.V))

    @property
    def note(self) -> str:
        return freq_to_note(self.f_H)

    def __repr__(self):
        return f"Cabaca('{self.name}', f_H={self.f_H:.1f} Hz, {self.note})"


def freq_to_note(freq: float) -> str:
    note_names = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
    semitones = 12 * math.log2(freq / 440.0) + 69
    midi = round(semitones)
    cents = round((semitones - midi) * 100)
    name = note_names[midi % 12]
    octave = midi // 12 - 1
    sign = '+' if cents >= 0 else ''
    return f"{name}{octave} ({sign}{cents}c)"
