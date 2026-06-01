"""
Prueba de reproducción de tonos por instrumento.

Uso:
    python tests/audio/tono.py               # todos los instrumentos disponibles
    python tests/audio/tono.py piano         # solo piano
    python tests/audio/tono.py piano 440     # piano, La4 (440 Hz)

Añadir samples:
    Descarga WAVs con nombre de nota (A4.wav, C3.wav, F#5.wav) y deposítalos en:
    lutheria_app/audio/samples/<instrumento>/
    Fuentes libres: University of Iowa EMF, Freesound (CC0), MIDI.js soundfonts.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lutheria_app'))

from audio.tono import available_instruments, play_note

NOTAS = [
    ('Do4',  261.63),
    ('Mi4',  329.63),
    ('Sol4', 392.00),
    ('La4',  440.00),
    ('Do5',  523.25),
]


def main():
    instruments = available_instruments()
    print(f"Instrumentos disponibles: {instruments}\n")

    selected = [sys.argv[1]] if len(sys.argv) > 1 else instruments
    freq_override = float(sys.argv[2]) if len(sys.argv) > 2 else None

    for instr in selected:
        print(f"--- {instr} ---")
        notas = [('manual', freq_override)] if freq_override else NOTAS
        for nombre, freq in notas:
            print(f"  {nombre} ({freq:.2f} Hz) ... ", end='', flush=True)
            try:
                play_note(freq, duration=1.5, instrument=instr)
                print("OK")
            except Exception as e:
                print(f"ERROR: {e}")
        print()


if __name__ == '__main__':
    main()
