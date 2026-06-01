import io
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import rfft, rfftfreq

IS_ANDROID = 'ANDROID_DATA' in os.environ

try:
    import sounddevice as sd
except Exception:
    sd = None

AUDIO_AVAILABLE = IS_ANDROID or (sd is not None)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.cabaca import freq_to_note

SAMPLE_RATE  = 44100
DURATION     = 3.0
F_MIN, F_MAX = 50, 1200
HARM_TOL     = 0.04
MIN_GROUP    = 2

GROUP_COLORS = ["#f0a500", "#81c784", "#4fc3f7", "#ce93d8", "#ff8a65"]
NOISE_COLOR  = "#444444"



def scale_color(hex_color: str, intensity: float) -> str:
    r, g, b = mcolors.to_rgb(hex_color)
    factor = 0.35 + 0.65 * intensity
    return mcolors.to_hex((r * factor, g * factor, b * factor))


def detect_f1(audio: np.ndarray, f_min: float = 80, f_max: float = 600) -> float | None:
    """Detecta la frecuencia fundamental dominante en el rango dado."""
    window = np.hanning(len(audio))
    freqs  = rfftfreq(len(audio), 1 / SAMPLE_RATE)
    mags   = np.abs(rfft(audio * window))
    mask   = (freqs >= f_min) & (freqs <= f_max)
    if not np.any(mask):
        return None
    peak_amp = mags[mask].max()
    if peak_amp < mags.max() * 0.05:
        return None
    return float(freqs[mask][np.argmax(mags[mask])])


def record_audio() -> np.ndarray:
    if not AUDIO_AVAILABLE:
        raise RuntimeError("Audio no disponible en este dispositivo")
    if IS_ANDROID:
        from audio.android_audio import android_record_audio
        return android_record_audio()
    audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE,
                   channels=1, dtype='float32')
    sd.wait()
    return audio[:, 0]


def find_peaks(freqs, mags, n=10, threshold=0.04) -> list[tuple[float, float]]:
    mask = (freqs >= F_MIN) & (freqs <= F_MAX)
    f, m = freqs[mask], mags[mask]
    if len(m) == 0 or m.max() == 0:
        return []
    min_amp = m.max() * threshold
    result = []
    for i in np.argsort(m)[::-1]:
        if m[i] < min_amp:
            break
        if all(abs(f[i] - p) > 15 for p, _ in result):
            result.append((float(f[i]), float(m[i])))
        if len(result) == n:
            break
    return result


def find_harmonic_groups(peaks):
    """
    Agrupa picos en series armónicas.
    Retorna (groups, ungrouped):
      groups    = [ [(freq, amp, n), ...], ... ]  orden desc. por energía
      ungrouped = []  (picos solitarios van como grupos de tamaño 1)
    """
    remaining = sorted(peaks, key=lambda x: x[0])
    groups = []
    while True:
        best_f0, best_group, best_score = None, {}, 0
        for f0, _ in remaining:
            candidate = {}
            for f, amp in remaining:
                ratio = f / f0
                n = round(ratio)
                if n >= 1 and abs(ratio - n) < HARM_TOL:
                    if n not in candidate:
                        candidate[n] = (f, amp)
            if len(candidate) > best_score:
                best_score = len(candidate)
                best_f0, best_group = f0, candidate
        if best_score < MIN_GROUP:
            break
        group_peaks = [(f, a, n) for n, (f, a) in best_group.items()]
        groups.append(group_peaks)
        assigned = {f for f, _, _ in group_peaks}
        remaining = [(f, a) for f, a in remaining if f not in assigned]
    for f, amp in remaining:
        groups.append([(f, amp, 1)])
    groups.sort(key=lambda g: sum(a for _, a, _ in g), reverse=True)
    return groups, []


def weights(groups, ungrouped):
    total_amp = sum(a for g in groups for _, a, _ in g) + sum(a for _, a in ungrouped)
    if total_amp == 0:
        return 0.0, [0.0] * len(groups), [[0.0] * len(g) for g in groups], 0.0
    group_share = [sum(a for _, a, _ in g) / total_amp for g in groups]
    peak_share  = [[a / (sum(aa for _, aa, _ in g) or 1.0) for _, a, _ in g] for g in groups]
    noise_share = sum(a for _, a in ungrouped) / total_amp if ungrouped else 0.0
    return total_amp, group_share, peak_share, noise_share


def process_and_plot(audio: np.ndarray):
    window = np.hanning(len(audio))
    freqs  = rfftfreq(len(audio), 1 / SAMPLE_RATE)
    mags   = np.abs(rfft(audio * window))
    peaks  = find_peaks(freqs, mags)
    groups, ungrouped = find_harmonic_groups(peaks)
    _, group_share, peak_share, noise_share = weights(groups, ungrouped)
    b64 = plot_spectrum(freqs, mags, groups, ungrouped, group_share, peak_share)
    return groups, ungrouped, group_share, peak_share, noise_share, b64


def plot_spectrum(freqs, mags, groups, ungrouped, group_share, peak_share) -> str:
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 3.8), facecolor='#0d0d0d')
    ax.set_facecolor('#111111')

    mask = (freqs >= F_MIN) & (freqs <= F_MAX)
    f_plot, m_plot = freqs[mask], mags[mask]
    if len(f_plot) > 0:
        ax.plot(f_plot, m_plot, color='#1e3040', linewidth=1.0)
    top = float(m_plot.max()) if len(m_plot) > 0 else 0.0
    ax.set_ylim(0, top * 1.15 if top > 0 else 1.0)

    for gi, (group, g_share) in enumerate(zip(groups, group_share)):
        base_color = GROUP_COLORS[gi % len(GROUP_COLORS)]
        for (f, amp, n), p_share in zip(sorted(group, key=lambda x: x[2]), peak_share[gi]):
            color = scale_color(base_color, p_share)
            ax.axvline(f, color=base_color, linewidth=1.0, alpha=0.6 + 0.4 * p_share)
            near = (freqs >= f * 0.986) & (freqs <= f * 1.014)
            ax.fill_between(freqs[near], mags[near],
                            alpha=0.25 + 0.55 * p_share, color=base_color)
            note  = freq_to_note(f).split('(')[0].strip()
            label = f" {note} n={n}\n {f:.0f}Hz\n {p_share*100:.0f}%"
            ax.text(f, top * 0.97, label, color=color, fontsize=7,
                    rotation=90, va='top', linespacing=1.3)

    ax.set_xlabel('Frecuencia (Hz)', color='#aaa', fontsize=9)
    ax.set_ylabel('Amplitud', color='#aaa', fontsize=9)
    ax.tick_params(colors='#666', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')
    ax.grid(True, color='#1a1a1a', linewidth=0.5)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.93, bottom=0.20)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, facecolor='#0d0d0d')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
