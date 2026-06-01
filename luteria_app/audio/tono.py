import os

import numpy as np

IS_ANDROID = 'ANDROID_DATA' in os.environ

try:
    import sounddevice as sd
except Exception:
    sd = None

SAMPLE_RATE = 44100


class TonePlayer:
    """Oscilador continuo con frecuencia ajustable en tiempo real."""

    def __new__(cls):
        if IS_ANDROID:
            from audio.android_audio import AndroidTonePlayer
            return AndroidTonePlayer()
        return super().__new__(cls)

    def __init__(self):
        self.freq   = 440.0
        self.phase  = 0
        self.stream = None

    def _callback(self, outdata, frames, time, status):
        t = (self.phase + np.arange(frames)) / SAMPLE_RATE
        outdata[:, 0] = 0.4 * np.sin(2 * np.pi * self.freq * t).astype(np.float32)
        self.phase += frames

    def start(self, freq: float):
        if sd is None:
            raise RuntimeError("Audio no disponible en este dispositivo")
        self.freq   = freq
        self.phase  = 0
        self.stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels=1,
                                      dtype='float32', callback=self._callback)
        self.stream.start()

    def set_freq(self, freq: float):
        self.freq = freq

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None


def generate_chirp(f_min: float, f_max: float, duration: float, vol: float = 0.7) -> np.ndarray:
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n) / SAMPLE_RATE
    phase = 2 * np.pi * (f_min * t + (f_max - f_min) * t**2 / (2 * duration))
    return (vol * np.sin(phase)).astype(np.float32)
