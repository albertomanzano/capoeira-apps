"""
Medición de f_H (resonancia de Helmholtz) de una cabaça.

Métodos:
  --ref     Chirp de referencia: dos tomas (sin/con cabaça), sustracción de sala.
  --golpe   Golpe o soplido: graba el decay/tono natural de la cabaça.
  --h1      H1 clásico con promediado.
  --search  Búsqueda iterativa: barrido amplio → candidatos → zoom → ganador.

Uso:
    python tests/models/cabaca.py --ref    200 900 1600 88
    python tests/models/cabaca.py --golpe  1600 88
    python tests/models/cabaca.py --h1     200 900 1600 88 5
    python tests/models/cabaca.py --search 200 1000 1600 88
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lutheria_app'))

import numpy as np
import sounddevice as sd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq

from audio.tono import generate_chirp, SAMPLE_RATE
from models.cabaca import Cabaca, freq_to_note

WARMUP    = 0.3
PAUSE     = 0.5
OUT_FILE  = '/tmp/cabaca_resonancia.png'

CHIRP_VOL_REF = 0.25   # volumen bajo para método de referencia
CHIRP_VOL_H1  = 0.70   # volumen estándar para H1
N_AVG_DEFAULT = 5
COH_MIN       = 0.5

SEARCH_N_BROAD = 10    # sweeps fase 1 (amplio)
SEARCH_N_ZOOM  = 20    # sweeps fase 2 (zoom)
SEARCH_N_CANDS = 3     # candidatos máximos
SEARCH_ZOOM_HZ = 70    # semi-anchura del zoom (±Hz)


# ── utilidades comunes ────────────────────────────────────────────────────────

def _cabaca_info(V_ml, d_mm):
    if V_ml and d_mm:
        return Cabaca('test', V_ml, d_mm)
    return None


def _plot_save(fig):
    plt.tight_layout(pad=1.2)
    fig.savefig(OUT_FILE, dpi=130, facecolor='#0d0d0d')
    plt.close(fig)
    print(f"Gráfica guardada en {OUT_FILE}")


def _dark_ax(ax):
    ax.set_facecolor('#111111')
    ax.tick_params(colors='#666', labelsize=8)
    for sp in ax.spines.values():
        sp.set_edgecolor('#333')
    ax.grid(True, color='#1a1a1a', linewidth=0.5)


def _mark_peak(ax, f_H, ymax=1.0):
    ax.axvline(f_H, color='#f0a500', linewidth=1.5, linestyle='--')
    ax.text(f_H + 4, ymax * 0.96,
            f'{f_H:.0f} Hz\n{freq_to_note(f_H).split("(")[0].strip()}',
            color='#f0a500', fontsize=9, va='top')


def _mark_theory(ax, cab):
    if cab:
        ax.axvline(cab.f_H, color='#81c784', linewidth=1.0, linestyle=':',
                   label=f'Teórica {cab.f_H:.0f} Hz')


def _print_result(f_H, cab):
    print(f"\nf_H medida:   {f_H:.1f} Hz → {freq_to_note(f_H)}")
    if cab:
        cents = 1200 * np.log2(f_H / cab.f_H)
        print(f"f_H teórica:  {cab.f_H:.1f} Hz → {cab.note}")
        print(f"Diferencia:   {cents:+.0f} cents")


# ── método referencia ─────────────────────────────────────────────────────────

def _sweep_h1(chirp_out):
    rec = sd.playrec(chirp_out, SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    n_trim   = int(WARMUP * SAMPLE_RATE)
    played   = chirp_out[n_trim:]
    recorded = rec[n_trim:, 0]
    n        = min(len(played), len(recorded))
    X        = rfft(played[:n])
    Y        = rfft(recorded[:n])
    Sxy      = np.conj(X) * Y
    Sxx      = (X * np.conj(X)).real
    Syy      = (Y * np.conj(Y)).real
    return Sxy, Sxx, Syy, rfftfreq(n, 1 / SAMPLE_RATE)


def _avg_sweeps(chirp_out, n, label):
    Sxy_s, Sxx_s, Syy_s, freqs = None, None, None, None
    for i in range(n):
        print(f"  {label} {i+1}/{n}...", end=' ', flush=True)
        Sxy, Sxx, Syy, freqs = _sweep_h1(chirp_out)
        if Sxy_s is None:
            Sxy_s, Sxx_s, Syy_s = Sxy.copy(), Sxx.copy(), Syy.copy()
        else:
            Sxy_s += Sxy; Sxx_s += Sxx; Syy_s += Syy
        print("OK")
        if i < n - 1:
            time.sleep(PAUSE)
    H1  = np.abs(Sxy_s) / (Sxx_s + 1e-10)
    coh = np.abs(Sxy_s) ** 2 / ((Sxx_s * Syy_s) + 1e-10)
    return H1, np.clip(coh, 0, 1), freqs


def medir_referencia(f_min=200., f_max=900., V_ml=None, d_mm=None, n_avg=3):
    cab = _cabaca_info(V_ml, d_mm)
    print(f"\n[Método referencia]  {f_min:.0f}–{f_max:.0f} Hz | {n_avg} sweeps × 2 tomas")
    print(f"Volumen bajo ({CHIRP_VOL_REF:.0%}) — deja espacio para que el efecto cabaça sea visible.")
    if cab:
        print(f"Predicción teórica: {cab.f_H:.1f} Hz → {cab.note}")

    chirp_out = generate_chirp(f_min, f_max, WARMUP + 5.0) * (CHIRP_VOL_REF / 0.7)

    print("\n1/2  REFERENCIA — aleja la cabaça del altavoz (>30 cm).")
    input("Pulsa Enter cuando esté lista la referencia...")
    H_ref, _, freqs = _avg_sweeps(chirp_out, n_avg, "ref")

    print("\n2/2  CABAÇA — coloca la cabaça a ~5 cm del altavoz, boca hacia él.")
    input("Pulsa Enter cuando esté lista la cabaça...")
    H_cab, coh, _  = _avg_sweeps(chirp_out, n_avg, "cab")

    # Ratio: efecto neto de la cabaça
    ratio = H_cab / (H_ref + 1e-10)

    mask    = (freqs >= f_min) & (freqs <= f_max)
    f_plot  = freqs[mask]
    R_plot  = ratio[mask]
    C_plot  = coh[mask]

    # Pico en zona de coherencia ≥ COH_MIN
    valid   = C_plot >= COH_MIN
    R_valid = np.where(valid, R_plot, 0)
    idx     = np.argmax(R_valid) if valid.any() else np.argmax(R_plot)
    f_H     = f_plot[idx]

    _print_result(f_H, cab)

    # ── gráfica ──
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), facecolor='#0d0d0d',
                                   gridspec_kw={'height_ratios': [2, 1]})
    R_norm = R_plot / R_plot.max()
    ax1.plot(f_plot, R_norm, color='#f0a500', linewidth=1.5,
             label=f'H_cab / H_ref  ({n_avg} avg)')
    ax1.axhline(1.0, color='#444', linewidth=0.6, linestyle='--')
    _mark_peak(ax1, f_H)
    _mark_theory(ax1, cab)
    ax1.set_ylabel('Ratio cab/ref (norm.)', color='#aaa', fontsize=9)
    ax1.set_title('Resonancia de Helmholtz — sustracción de referencia', color='white', fontsize=11)
    ax1.legend(fontsize=8, facecolor='#1a1a1a', edgecolor='#333')
    _dark_ax(ax1); ax1.set_xlim(f_plot[0], f_plot[-1])

    ax2.fill_between(f_plot, C_plot, alpha=0.4, color='#ce93d8')
    ax2.plot(f_plot, C_plot, color='#ce93d8', linewidth=1.2, label='Coherencia γ²')
    ax2.axhline(COH_MIN, color='#666', linewidth=0.8, linestyle='--',
                label=f'umbral {COH_MIN}')
    ax2.axvline(f_H, color='#f0a500', linewidth=1.5, linestyle='--')
    ax2.set_ylim(0, 1.05)
    ax2.set_xlabel('Frecuencia (Hz)', color='#aaa', fontsize=9)
    ax2.set_ylabel('γ²(f)', color='#aaa', fontsize=9)
    ax2.legend(fontsize=8, facecolor='#1a1a1a', edgecolor='#333')
    _dark_ax(ax2); ax2.set_xlim(f_plot[0], f_plot[-1])

    _plot_save(fig)


# ── método golpe/soplido ──────────────────────────────────────────────────────

def medir_golpe(V_ml=None, d_mm=None, duration=3.0, f_min=80., f_max=1200.):
    cab = _cabaca_info(V_ml, d_mm)
    print(f"\n[Método golpe/soplido]  grabación {duration}s")
    if cab:
        print(f"Predicción teórica: {cab.f_H:.1f} Hz → {cab.note}")
    print("\nOpciones:")
    print("  · Golpe: da un toque seco en el cuerpo de la cabaça")
    print("  · Soplido: sopla suavemente a través de la boca")
    input("Pulsa Enter y actúa en los primeros 2 segundos...")

    audio = sd.rec(int(SAMPLE_RATE * duration), samplerate=SAMPLE_RATE,
                   channels=1, dtype='float32')
    sd.wait()
    audio = audio[:, 0]

    # Detectar onset (golpe) o usar señal completa (soplido)
    onset = _find_onset(audio)
    if onset is not None:
        skip  = onset + int(0.008 * SAMPLE_RATE)   # salta 8ms de click del golpe
        segment = audio[skip: skip + int(1.0 * SAMPLE_RATE)]
        mode  = 'golpe'
    else:
        segment = audio                              # señal completa (soplido)
        mode  = 'soplido'

    print(f"  Modo detectado: {mode}")

    window = np.hanning(len(segment))
    freqs  = rfftfreq(len(segment), 1 / SAMPLE_RATE)
    mags   = np.abs(rfft(segment * window))

    mask   = (freqs >= f_min) & (freqs <= f_max)
    f_plot = freqs[mask]
    m_plot = mags[mask]
    idx    = np.argmax(m_plot)
    f_H    = f_plot[idx]

    _print_result(f_H, cab)

    # ── gráfica ──
    fig, ax = plt.subplots(figsize=(9, 4), facecolor='#0d0d0d')
    m_norm  = m_plot / m_plot.max()
    ax.plot(f_plot, m_norm, color='#81c784', linewidth=1.3,
            label=f'Espectro ({mode})')
    _mark_peak(ax, f_H)
    _mark_theory(ax, cab)
    ax.set_xlabel('Frecuencia (Hz)', color='#aaa', fontsize=9)
    ax.set_ylabel('Amplitud (norm.)', color='#aaa', fontsize=9)
    ax.set_title(f'Resonancia de Helmholtz — {mode}', color='white', fontsize=11)
    ax.legend(fontsize=8, facecolor='#1a1a1a', edgecolor='#333')
    _dark_ax(ax)
    _plot_save(fig)


def _find_onset(audio, noise_window=0.1, factor=8.0):
    """Detecta el inicio de un golpe. Devuelve índice o None si no hay onset claro."""
    n_noise   = int(noise_window * SAMPLE_RATE)
    rms_noise = np.sqrt(np.mean(audio[:n_noise] ** 2))
    threshold = rms_noise * factor
    above     = np.where(np.abs(audio) > threshold)[0]
    if len(above) == 0:
        return None
    # Verifica que el máximo también supera el threshold (no es ruido puntual)
    if np.abs(audio).max() < threshold * 1.5:
        return None
    return int(above[0])


# ── método H1 (original mejorado) ────────────────────────────────────────────

def medir_h1(f_min=200., f_max=900., V_ml=None, d_mm=None, n_avg=N_AVG_DEFAULT):
    cab = _cabaca_info(V_ml, d_mm)
    print(f"\n[Método H1]  {f_min:.0f}–{f_max:.0f} Hz | {n_avg} sweeps")
    if cab:
        print(f"Predicción teórica: {cab.f_H:.1f} Hz → {cab.note}")
    print("\nColoca el altavoz ~5 cm de la boca de la cabaça apuntando hacia dentro.")
    input("Pulsa Enter para empezar...")

    chirp_out       = generate_chirp(f_min, f_max, WARMUP + 5.0)
    H1, coh, freqs  = _avg_sweeps(chirp_out, n_avg, "sweep")

    mask   = (freqs >= f_min) & (freqs <= f_max)
    f_plot = freqs[mask]
    H_plot = H1[mask]
    C_plot = coh[mask]

    valid  = C_plot >= COH_MIN
    idx    = np.argmax(np.where(valid, H_plot, 0)) if valid.any() else np.argmax(H_plot)
    f_H    = f_plot[idx]
    if not valid.any():
        print("  Aviso: coherencia baja — acerca más el altavoz o baja el volumen del entorno")

    _print_result(f_H, cab)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), facecolor='#0d0d0d',
                                   gridspec_kw={'height_ratios': [2, 1]})
    H_norm = H_plot / H_plot.max()
    ax1.plot(f_plot, H_norm, color='#4fc3f7', linewidth=1.5, label=f'H1 ({n_avg} avg)')
    _mark_peak(ax1, f_H)
    _mark_theory(ax1, cab)
    ax1.set_ylabel('H1(f) normalizada', color='#aaa', fontsize=9)
    ax1.set_title('Resonancia de Helmholtz — H1', color='white', fontsize=11)
    ax1.legend(fontsize=8, facecolor='#1a1a1a', edgecolor='#333')
    _dark_ax(ax1); ax1.set_xlim(f_plot[0], f_plot[-1])

    ax2.fill_between(f_plot, C_plot, alpha=0.4, color='#ce93d8')
    ax2.plot(f_plot, C_plot, color='#ce93d8', linewidth=1.2, label='Coherencia γ²')
    ax2.axhline(COH_MIN, color='#666', linewidth=0.8, linestyle='--')
    ax2.axvline(f_H, color='#f0a500', linewidth=1.5, linestyle='--')
    ax2.set_ylim(0, 1.05)
    ax2.set_xlabel('Frecuencia (Hz)', color='#aaa', fontsize=9)
    ax2.set_ylabel('γ²(f)', color='#aaa', fontsize=9)
    ax2.legend(fontsize=8, facecolor='#1a1a1a', edgecolor='#333')
    _dark_ax(ax2); ax2.set_xlim(f_plot[0], f_plot[-1])
    _plot_save(fig)


# ── búsqueda iterativa ────────────────────────────────────────────────────────

def medir_search(f_min=200., f_max=1000., V_ml=None, d_mm=None):
    from scipy.signal import find_peaks as sp_find_peaks

    cab = _cabaca_info(V_ml, d_mm)
    print(f"\n[Búsqueda iterativa]  {f_min:.0f}–{f_max:.0f} Hz")
    if cab:
        print(f"Predicción teórica: {cab.f_H:.1f} Hz → {cab.note}")

    # ── Fase 1: barrido amplio ─────────────────────────────────────────────────
    print(f"\nFase 1 — barrido amplio ({SEARCH_N_BROAD} sweeps, {f_min:.0f}–{f_max:.0f} Hz)")
    input("Pulsa Enter para empezar...")

    chirp_broad = generate_chirp(f_min, f_max, WARMUP + 5.0)
    H1, coh, freqs = _avg_sweeps(chirp_broad, SEARCH_N_BROAD, "broad")

    mask = (freqs >= f_min) & (freqs <= f_max)
    fb, Hb, Cb = freqs[mask], H1[mask], np.clip(coh[mask], 0, 1)
    Hb_norm = Hb / (Hb.max() + 1e-10)

    # Candidatos: máximos locales en H1_norm × coh (solo donde coh > umbral)
    score = Hb_norm * np.where(Cb >= COH_MIN, Cb, 0)
    df = float(fb[1] - fb[0]) if len(fb) > 1 else 1.0
    min_dist = max(1, int(50 / df))
    peak_idxs, _ = sp_find_peaks(score, distance=min_dist, height=1e-3)
    peak_idxs = sorted(peak_idxs, key=lambda i: score[i], reverse=True)[:SEARCH_N_CANDS]

    if not peak_idxs:
        valid = Cb >= COH_MIN
        peak_idxs = [int(np.argmax(np.where(valid, Hb, 0))) if valid.any() else int(np.argmax(Hb))]

    candidates = [(float(fb[i]), float(Cb[i]), float(Hb_norm[i])) for i in peak_idxs]
    print(f"\nCandidatos detectados:")
    for i, (f, c, h) in enumerate(candidates):
        print(f"  C{i+1}: {f:.0f} Hz  coh={c:.2f}  H1={h:.2f}")

    # ── Fase 2: zoom en cada candidato ────────────────────────────────────────
    print(f"\nFase 2 — zoom ±{SEARCH_ZOOM_HZ} Hz en cada candidato ({SEARCH_N_ZOOM} sweeps × {len(candidates)})")
    zoom_results = []
    for i, (f_c, _, _) in enumerate(candidates):
        fz_min = max(f_min, f_c - SEARCH_ZOOM_HZ)
        fz_max = min(f_max, f_c + SEARCH_ZOOM_HZ)
        print(f"\nZoom C{i+1}: {fz_min:.0f}–{fz_max:.0f} Hz")
        chirp_z = generate_chirp(fz_min, fz_max, WARMUP + 3.0)
        Hz, cohz, freqsz = _avg_sweeps(chirp_z, SEARCH_N_ZOOM, f"C{i+1}")

        maskz = (freqsz >= fz_min) & (freqsz <= fz_max)
        fz = freqsz[maskz]
        Hz_p = Hz[maskz]
        Cz_p = np.clip(cohz[maskz], 0, 1)
        Hz_norm = Hz_p / (Hz_p.max() + 1e-10)

        validz = Cz_p >= COH_MIN
        score_z = Hz_norm * np.where(validz, Cz_p, 0)
        idxz = int(np.argmax(score_z)) if score_z.max() > 0 else int(np.argmax(Hz_p))
        f_ref = float(fz[idxz])
        c_ref = float(Cz_p[idxz])
        h_ref = float(Hz_norm[idxz])
        score_ref = h_ref * c_ref
        print(f"  → {f_ref:.1f} Hz  coh={c_ref:.2f}  H1={h_ref:.2f}  score={score_ref:.2f}")
        zoom_results.append((fz, Hz_norm, Cz_p, f_ref, c_ref, h_ref))

    # ── Ganador: mayor H1×coherencia en el pico refinado ─────────────────────
    winner_idx = max(range(len(zoom_results)), key=lambda i: zoom_results[i][4] * zoom_results[i][5])
    f_H = zoom_results[winner_idx][3]
    print(f"\n{'='*50}")
    _print_result(f_H, cab)

    # ── Gráfica ───────────────────────────────────────────────────────────────
    n_c = len(zoom_results)
    fig = plt.figure(figsize=(max(9, 4 * n_c), 10), facecolor='#0d0d0d')
    gs  = plt.GridSpec(4, n_c, figure=fig,
                       height_ratios=[2, 1, 2, 1], hspace=0.55, wspace=0.35)

    # Barrido amplio
    ax_b1 = fig.add_subplot(gs[0, :])
    ax_b2 = fig.add_subplot(gs[1, :])

    ax_b1.plot(fb, Hb_norm, color='#4fc3f7', linewidth=1.2,
               label=f'H1 amplio ({SEARCH_N_BROAD} avg)')
    for i, (fc, _, _) in enumerate(candidates):
        col = '#f0a500' if i == winner_idx else '#888888'
        ax_b1.axvline(fc, color=col, linewidth=1.2, linestyle='--', alpha=0.8)
        ax_b1.text(fc + 3, 0.95, f'C{i+1}', color=col, fontsize=8, va='top')
    _mark_theory(ax_b1, cab)
    ax_b1.set_ylabel('H1 norm.', color='#aaa', fontsize=9)
    ax_b1.set_title('Búsqueda iterativa — barrido amplio', color='white', fontsize=11)
    ax_b1.legend(fontsize=8, facecolor='#1a1a1a', edgecolor='#333')
    _dark_ax(ax_b1); ax_b1.set_xlim(fb[0], fb[-1])

    ax_b2.fill_between(fb, Cb, alpha=0.35, color='#ce93d8')
    ax_b2.plot(fb, Cb, color='#ce93d8', linewidth=1.0, label='Coherencia γ²')
    ax_b2.axhline(COH_MIN, color='#666', linewidth=0.8, linestyle='--',
                  label=f'umbral {COH_MIN}')
    for i, (fc, _, _) in enumerate(candidates):
        col = '#f0a500' if i == winner_idx else '#888888'
        ax_b2.axvline(fc, color=col, linewidth=1.2, linestyle='--', alpha=0.8)
    ax_b2.set_ylim(0, 1.05)
    ax_b2.set_xlabel('Frecuencia (Hz)', color='#aaa', fontsize=9)
    ax_b2.set_ylabel('γ²', color='#aaa', fontsize=9)
    ax_b2.legend(fontsize=8, facecolor='#1a1a1a', edgecolor='#333')
    _dark_ax(ax_b2); ax_b2.set_xlim(fb[0], fb[-1])

    # Zooms por candidato
    for i, (fz, Hz_norm, Cz_p, f_ref, c_ref, h_ref) in enumerate(zoom_results):
        is_winner = (i == winner_idx)
        col   = '#f0a500' if is_winner else '#81c784'
        label = f'C{i+1}: {f_ref:.0f} Hz' + (' ★' if is_winner else '')

        ax_z1 = fig.add_subplot(gs[2, i])
        ax_z1.plot(fz, Hz_norm, color=col, linewidth=1.3, label=label)
        ax_z1.axvline(f_ref, color=col, linewidth=1.5, linestyle='--')
        ax_z1.text(f_ref + 1, 0.95,
                   f'{f_ref:.0f} Hz\n{freq_to_note(f_ref).split("(")[0].strip()}',
                   color=col, fontsize=8, va='top')
        ax_z1.set_ylabel('H1 norm.', color='#aaa', fontsize=8)
        ax_z1.set_title(('GANADOR — ' if is_winner else '') + f'C{i+1}',
                        color=col, fontsize=9)
        ax_z1.legend(fontsize=7, facecolor='#1a1a1a', edgecolor='#333')
        _dark_ax(ax_z1); ax_z1.set_xlim(fz[0], fz[-1])

        ax_z2 = fig.add_subplot(gs[3, i])
        ax_z2.fill_between(fz, Cz_p, alpha=0.35, color=col)
        ax_z2.plot(fz, Cz_p, color=col, linewidth=1.0, label=f'coh={c_ref:.2f}')
        ax_z2.axhline(COH_MIN, color='#666', linewidth=0.8, linestyle='--')
        ax_z2.axvline(f_ref, color=col, linewidth=1.5, linestyle='--')
        ax_z2.set_ylim(0, 1.05)
        ax_z2.set_xlabel('Hz', color='#aaa', fontsize=8)
        ax_z2.set_ylabel('γ²', color='#aaa', fontsize=8)
        ax_z2.legend(fontsize=7, facecolor='#1a1a1a', edgecolor='#333')
        _dark_ax(ax_z2); ax_z2.set_xlim(fz[0], fz[-1])

    _plot_save(fig)


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args   = sys.argv[1:]
    method = args[0] if args and args[0].startswith('--') else '--h1'
    rest   = args[1:] if args and args[0].startswith('--') else args

    if method == '--ref':
        f_min = float(rest[0]) if len(rest) > 0 else 200.
        f_max = float(rest[1]) if len(rest) > 1 else 900.
        V_ml  = float(rest[2]) if len(rest) > 2 else None
        d_mm  = float(rest[3]) if len(rest) > 3 else None
        n_avg = int(rest[4])   if len(rest) > 4 else 3
        medir_referencia(f_min, f_max, V_ml, d_mm, n_avg)

    elif method == '--golpe':
        V_ml = float(rest[0]) if len(rest) > 0 else None
        d_mm = float(rest[1]) if len(rest) > 1 else None
        medir_golpe(V_ml, d_mm)

    elif method == '--search':
        f_min = float(rest[0]) if len(rest) > 0 else 200.
        f_max = float(rest[1]) if len(rest) > 1 else 1000.
        V_ml  = float(rest[2]) if len(rest) > 2 else None
        d_mm  = float(rest[3]) if len(rest) > 3 else None
        medir_search(f_min, f_max, V_ml, d_mm)

    else:  # --h1
        f_min = float(rest[0]) if len(rest) > 0 else 200.
        f_max = float(rest[1]) if len(rest) > 1 else 900.
        V_ml  = float(rest[2]) if len(rest) > 2 else None
        d_mm  = float(rest[3]) if len(rest) > 3 else None
        n_avg = int(rest[4])   if len(rest) > 4 else N_AVG_DEFAULT
        medir_h1(f_min, f_max, V_ml, d_mm, n_avg)
