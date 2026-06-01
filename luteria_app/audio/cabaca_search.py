import numpy as np
from numpy.fft import rfft, rfftfreq

try:
    import sounddevice as sd
except Exception:
    sd = None

from audio.tono import SAMPLE_RATE, generate_chirp

WARMUP          = 0.3
N_BROAD         = 6
N_ZOOM          = 10
N_CANDS         = 2
ZOOM_HZ         = 60
COH_MIN         = 0.5
CHIRP_BROAD_DUR = 4.0
CHIRP_ZOOM_DUR  = 2.0
F_MIN           = 100.0
F_MAX           = 800.0


def sweep_h1_once(chirp_out: np.ndarray):
    """Un playrec: emite chirp y graba simultáneamente. Devuelve (Sxy, Sxx, Syy, freqs)."""
    if sd is None:
        raise RuntimeError("sounddevice no disponible")
    rec      = sd.playrec(chirp_out, SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    n_trim   = int(WARMUP * SAMPLE_RATE)
    played   = chirp_out[n_trim:]
    recorded = rec[n_trim:, 0]
    n        = min(len(played), len(recorded))
    X   = rfft(played[:n])
    Y   = rfft(recorded[:n])
    Sxy = np.conj(X) * Y
    Sxx = (X * np.conj(X)).real
    Syy = (Y * np.conj(Y)).real
    return Sxy, Sxx, Syy, rfftfreq(n, 1 / SAMPLE_RATE)


def accumulate(acc, Sxy, Sxx, Syy):
    if acc is None:
        return Sxy.copy(), Sxx.copy(), Syy.copy()
    return acc[0] + Sxy, acc[1] + Sxx, acc[2] + Syy


def finalize(acc, freqs):
    Sxy_s, Sxx_s, Syy_s = acc
    H1  = np.abs(Sxy_s) / (Sxx_s + 1e-10)
    coh = np.abs(Sxy_s)**2 / ((Sxx_s * Syy_s) + 1e-10)
    return H1, np.clip(coh, 0, 1), freqs


def find_candidates(H1, coh, freqs, f_min, f_max):
    mask    = (freqs >= f_min) & (freqs <= f_max)
    fb, Hb, Cb = freqs[mask], H1[mask], coh[mask]
    Hb_norm = Hb / (Hb.max() + 1e-10)
    score   = Hb_norm * np.where(Cb >= COH_MIN, Cb, 0)
    df      = float(fb[1] - fb[0]) if len(fb) > 1 else 1.0
    min_gap = max(1, int(50 / df))
    result  = []
    for idx in np.argsort(score)[::-1]:
        if score[idx] <= 1e-3:
            break
        if all(abs(int(idx) - j) >= min_gap for j in result):
            result.append(int(idx))
        if len(result) == N_CANDS:
            break
    return [float(fb[i]) for i in result] or [float(fb[int(np.argmax(Hb_norm))])]


def zoom_winner(H1, coh, freqs, fz_min, fz_max):
    mask    = (freqs >= fz_min) & (freqs <= fz_max)
    fz      = freqs[mask]
    Hz      = H1[mask]
    Cz      = np.clip(coh[mask], 0, 1)
    Hz_norm = Hz / (Hz.max() + 1e-10)
    score_z = Hz_norm * np.where(Cz >= COH_MIN, Cz, 0)
    idxz    = int(np.argmax(score_z)) if score_z.max() > 0 else int(np.argmax(Hz))
    return float(fz[idxz]), float(Cz[idxz])
