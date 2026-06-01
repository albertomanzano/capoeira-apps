"""
Calibración del analizador de espectro.

Reproduce un tono conocido por los altavoces mientras graba por el micrófono,
luego compara frecuencia emitida con frecuencia detectada usando detección
de grupos armónicos (no solo el pico más fuerte).

Uso:
    python tests/audio/espectro.py           # barrido completo con sine
    python tests/audio/espectro.py piano     # un instrumento
    python tests/audio/espectro.py all       # todos los instrumentos disponibles
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lutheria_app'))

import numpy as np
import sounddevice as sd
from scipy.fft import rfft, rfftfreq

from audio.tono import generate_samples, available_instruments, SAMPLE_RATE
from audio.espectro import find_peaks, find_harmonic_groups, a_weighted_rms
from models.cabaca import freq_to_note

NOTAS = [
    ('La2',  110.00),
    ('Mi3',  164.81),
    ('La3',  220.00),
    ('Do4',  261.63),
    ('Mi4',  329.63),
    ('La4',  440.00),
    ('Mi5',  659.25),
    ('La5',  880.00),
]

DURATION        = 1.5    # segundos de reproducción
WARMUP          = 0.2    # segundos descartados al inicio (latencia altavoz→micro)
TARGET_ALOUD    = 0.08   # loudness A-ponderada objetivo (≈ nivel conversacional cómodo)
MAX_GAIN        = 12.0   # límite de amplificación para no saturar en graves
THRESHOLD_CENTS = 20


def _normalize(audio: np.ndarray) -> np.ndarray:
    """
    Normaliza por loudness A-ponderada en lugar de RMS físico.
    Compensa la respuesta irregular del altavoz y la curva del oído,
    de modo que 110 Hz y 880 Hz suenan al mismo nivel percibido.
    """
    aw = a_weighted_rms(audio)
    if aw < 1e-10:
        return audio
    gain = min(TARGET_ALOUD / aw, MAX_GAIN)
    return (audio * gain).astype(np.float32)


def _detect_fundamental(audio: np.ndarray) -> tuple[float | None, float]:
    """
    Devuelve (f0 del grupo armónico dominante, rms grabado).

    Usa find_harmonic_groups para inferir el fundamental aunque no sea
    el parcial más fuerte. Si solo hay un pico (instrumento puro o señal
    débil), lo usa directamente como f0.
    """
    window = np.hanning(len(audio))
    freqs  = rfftfreq(len(audio), 1 / SAMPLE_RATE)
    mags   = np.abs(rfft(audio * window))
    rms    = float(np.sqrt(np.mean(audio ** 2)))

    peaks = find_peaks(freqs, mags, n=12, threshold=0.02)
    if not peaks:
        return None, rms

    groups, _ = find_harmonic_groups(peaks)
    if not groups:
        return None, rms

    dominant   = groups[0]
    f, _, n    = min(dominant, key=lambda x: x[2])   # parcial con n más bajo
    return f / n, rms                                 # f/n = f0 aunque falte n=1


def _cents(detected: float, emitted: float) -> float:
    return 1200 * np.log2(detected / emitted)


def calibrate(instrument: str = 'sine'):
    print(f"\nCalibración — instrumento: {instrument}")
    print(f"{'Nota':<8} {'Emitido (Hz)':>13} {'Detectado (Hz)':>15} {'Error':>10}  {'RMS':>7}  Estado")
    print("─" * 68)

    for nombre, freq_emitida in NOTAS:
        audio_out = _normalize(generate_samples(freq_emitida, DURATION, instrument))
        audio_rec = sd.playrec(audio_out, SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()

        audio_in         = audio_rec[int(WARMUP * SAMPLE_RATE):, 0]
        detected, rms_in = _detect_fundamental(audio_in)

        if detected is None:
            print(f"{nombre:<8} {freq_emitida:>13.2f} {'—':>15} {'—':>10}  {rms_in:>7.4f}  NO DETECTADO")
            continue

        error  = _cents(detected, freq_emitida)
        estado = "OK" if abs(error) <= THRESHOLD_CENTS else "WARN" if abs(error) <= 100 else "FAIL"
        print(f"{nombre:<8} {freq_emitida:>13.2f} {detected:>15.2f} {error:>+9.1f}¢  {rms_in:>7.4f}  {estado}")


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'sine'
    if arg == 'all':
        for instr in available_instruments():
            calibrate(instr)
    else:
        calibrate(arg)
