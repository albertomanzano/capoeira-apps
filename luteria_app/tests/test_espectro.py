import numpy as np
import pytest
from audio.espectro import (
    SAMPLE_RATE, F_MIN, F_MAX, HARM_TOL, MIN_GROUP,
    find_peaks, find_harmonic_groups, weights,
)


def _spectrum(freq_amp_pairs: list[tuple[float, float]], n: int = 132300):
    """Espectro sintético con picos en frecuencias dadas (Hz, amplitud)."""
    freqs = np.fft.rfftfreq(n, 1 / SAMPLE_RATE)
    mags  = np.zeros(len(freqs))
    for f, a in freq_amp_pairs:
        idx = int(np.argmin(np.abs(freqs - f)))
        mags[idx] = a
    return freqs, mags


# ---------------------------------------------------------------------------
# find_peaks
# ---------------------------------------------------------------------------

def test_find_peaks_empty_spectrum():
    freqs, mags = _spectrum([])
    assert find_peaks(freqs, mags) == []


def test_find_peaks_all_zeros():
    freqs = np.fft.rfftfreq(132300, 1 / SAMPLE_RATE)
    mags  = np.zeros(len(freqs))
    assert find_peaks(freqs, mags) == []


def test_find_peaks_single_peak():
    freqs, mags = _spectrum([(440.0, 1.0)])
    peaks = find_peaks(freqs, mags)
    assert len(peaks) == 1
    f, a = peaks[0]
    assert abs(f - 440.0) < 1.0
    assert a > 0


def test_find_peaks_filters_below_F_MIN():
    freqs, mags = _spectrum([(20.0, 1.0)])
    assert find_peaks(freqs, mags) == []


def test_find_peaks_filters_above_F_MAX():
    freqs, mags = _spectrum([(2000.0, 1.0)])
    assert find_peaks(freqs, mags) == []


def test_find_peaks_threshold_drops_weak_peaks():
    # Pico fuerte a 440 Hz, pico débil (< 4 %) a 880 Hz
    freqs, mags = _spectrum([(440.0, 1.0), (880.0, 0.03)])
    peaks = find_peaks(freqs, mags)
    found_freqs = [f for f, _ in peaks]
    assert any(abs(f - 440.0) < 1.0 for f in found_freqs)
    assert not any(abs(f - 880.0) < 1.0 for f in found_freqs)


def test_find_peaks_returns_at_most_n():
    pairs = [(100.0 + i * 30, 1.0) for i in range(20)]
    freqs, mags = _spectrum(pairs)
    peaks = find_peaks(freqs, mags, n=5)
    assert len(peaks) <= 5


def test_find_peaks_sorted_by_amplitude():
    freqs, mags = _spectrum([(300.0, 0.5), (500.0, 1.0), (700.0, 0.8)])
    peaks = find_peaks(freqs, mags)
    amps = [a for _, a in peaks]
    assert amps == sorted(amps, reverse=True)


def test_find_peaks_minimum_spacing():
    # Dos picos a 440 y 445 Hz: separación 5 Hz < umbral 15 Hz → solo el más alto
    freqs, mags = _spectrum([(440.0, 1.0), (445.0, 0.9)])
    peaks = find_peaks(freqs, mags)
    assert len(peaks) == 1


# ---------------------------------------------------------------------------
# find_harmonic_groups
# ---------------------------------------------------------------------------

def test_find_harmonic_groups_empty():
    groups, ungrouped = find_harmonic_groups([])
    assert groups == []
    assert ungrouped == []


def test_find_harmonic_groups_single_peak_becomes_solo_group():
    groups, ungrouped = find_harmonic_groups([(440.0, 1.0)])
    assert len(groups) == 1
    assert groups[0][0][2] == 1  # n = 1


def test_find_harmonic_groups_detects_harmonic_series():
    # Serie armónica perfecta: f0=200 Hz, n=1,2,3,4
    peaks = [(200.0, 1.0), (400.0, 0.8), (600.0, 0.6), (800.0, 0.4)]
    groups, _ = find_harmonic_groups(peaks)
    # Debe haber al menos un grupo con ≥ 2 armónicos
    assert any(len(g) >= 2 for g in groups)


def test_find_harmonic_groups_n_values_are_positive():
    peaks = [(200.0, 1.0), (400.0, 0.8), (600.0, 0.5)]
    groups, _ = find_harmonic_groups(peaks)
    for group in groups:
        for _, _, n in group:
            assert n >= 1


def test_find_harmonic_groups_groups_sorted_by_energy():
    # Grupo fuerte: 200/400/600 Hz. Grupo débil: 700/1050 Hz (no armónico entre sí).
    # Solo hay una serie armónica, la segunda no cumple MIN_GROUP=2.
    peaks = [(200.0, 1.0), (400.0, 0.8), (600.0, 0.6),
             (700.0, 0.1), (1050.0, 0.05)]
    groups, _ = find_harmonic_groups(peaks)
    if len(groups) >= 2:
        e0 = sum(a for _, a, _ in groups[0])
        e1 = sum(a for _, a, _ in groups[1])
        assert e0 >= e1


def test_find_harmonic_groups_all_peaks_accounted_for():
    peaks = [(200.0, 1.0), (400.0, 0.8), (550.0, 0.3)]
    groups, _ = find_harmonic_groups(peaks)
    total_in_groups = sum(len(g) for g in groups)
    assert total_in_groups == len(peaks)


# ---------------------------------------------------------------------------
# weights
# ---------------------------------------------------------------------------

def test_weights_empty_returns_zeros():
    total, g_share, p_share, noise = weights([], [])
    assert total == 0.0
    assert g_share == []
    assert p_share == []
    assert noise == 0.0


def test_weights_single_group_single_peak():
    groups = [[(440.0, 2.0, 1)]]
    total, g_share, p_share, noise = weights(groups, [])
    assert total == pytest.approx(2.0)
    assert g_share == [pytest.approx(1.0)]
    assert p_share == [[pytest.approx(1.0)]]
    assert noise == pytest.approx(0.0)


def test_weights_group_shares_sum_to_one():
    groups = [
        [(200.0, 3.0, 1), (400.0, 1.0, 2)],
        [(700.0, 2.0, 1)],
    ]
    _, g_share, _, _ = weights(groups, [])
    assert sum(g_share) == pytest.approx(1.0, rel=1e-6)


def test_weights_peak_shares_sum_to_one_per_group():
    groups = [[(200.0, 3.0, 1), (400.0, 1.0, 2), (600.0, 0.5, 3)]]
    _, _, p_share, _ = weights(groups, [])
    assert sum(p_share[0]) == pytest.approx(1.0, rel=1e-6)


def test_weights_no_division_by_zero_on_zero_amplitude():
    groups = [[(440.0, 0.0, 1)]]
    total, g_share, p_share, noise = weights(groups, [])
    assert total == pytest.approx(0.0)
    assert g_share == [pytest.approx(0.0)]
    # peak_share devuelve 0 sin lanzar excepción
    assert p_share[0][0] == pytest.approx(0.0)


def test_weights_proportional_group_shares():
    groups = [[(200.0, 3.0, 1)], [(700.0, 1.0, 1)]]
    _, g_share, _, _ = weights(groups, [])
    assert g_share[0] == pytest.approx(0.75, rel=1e-6)
    assert g_share[1] == pytest.approx(0.25, rel=1e-6)
