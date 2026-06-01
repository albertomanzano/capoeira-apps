import math
import pytest
from models.cabaca import Cabaca, freq_to_note

C_SOUND = 343.0


# ---------------------------------------------------------------------------
# freq_to_note: notas de referencia exactas
# ---------------------------------------------------------------------------

def test_freq_to_note_A4():
    assert freq_to_note(440.0).startswith("La4")

def test_freq_to_note_A3():
    assert freq_to_note(220.0).startswith("La3")

def test_freq_to_note_A5():
    assert freq_to_note(880.0).startswith("La5")

def test_freq_to_note_C4():
    assert freq_to_note(261.63).startswith("Do4")

def test_freq_to_note_E4():
    assert freq_to_note(329.63).startswith("Mi4")

def test_freq_to_note_zero_cents_at_exact_A4():
    result = freq_to_note(440.0)
    assert "(+0c)" in result

def test_freq_to_note_positive_cents_above_semitone():
    # 450 Hz está por encima de La4 (440 Hz)
    result = freq_to_note(450.0)
    assert "+" in result

def test_freq_to_note_negative_cents_below_semitone():
    # 430 Hz está por debajo de La4
    result = freq_to_note(430.0)
    assert result.count("-") >= 1

def test_freq_to_note_increases_with_octave():
    n3 = freq_to_note(220.0)
    n4 = freq_to_note(440.0)
    n5 = freq_to_note(880.0)
    assert "3" in n3 and "4" in n4 and "5" in n5


# ---------------------------------------------------------------------------
# Cabaca: fórmula de Helmholtz
# ---------------------------------------------------------------------------

def _expected_fH(V_ml, d_mm):
    V = V_ml * 1e-6
    r = (d_mm / 2) * 1e-3
    return (C_SOUND / (2 * math.pi)) * math.sqrt(math.pi * r / (0.85 * V))


def test_cabaca_fH_formula_reference():
    c = Cabaca("ref", V_ml=2600.0, d_mm=60.0)
    assert c.f_H == pytest.approx(_expected_fH(2600.0, 60.0), rel=1e-6)


def test_cabaca_fH_formula_small():
    c = Cabaca("small", V_ml=800.0, d_mm=40.0)
    assert c.f_H == pytest.approx(_expected_fH(800.0, 40.0), rel=1e-6)


def test_cabaca_fH_formula_large():
    c = Cabaca("large", V_ml=5000.0, d_mm=80.0)
    assert c.f_H == pytest.approx(_expected_fH(5000.0, 80.0), rel=1e-6)


def test_cabaca_fH_is_positive():
    c = Cabaca("x", V_ml=2000.0, d_mm=50.0)
    assert c.f_H > 0


def test_cabaca_uses_measured_fH_when_given():
    c = Cabaca("x", V_ml=2600.0, d_mm=60.0, f_H_measured=234.5)
    assert c.f_H == 234.5


def test_cabaca_calculated_fH_ignores_measurement_of_none():
    c = Cabaca("x", V_ml=2600.0, d_mm=60.0, f_H_measured=None)
    assert c.f_H == pytest.approx(_expected_fH(2600.0, 60.0), rel=1e-6)


def test_cabaca_larger_volume_lower_fH():
    c_small = Cabaca("s", V_ml=500.0,  d_mm=40.0)
    c_large = Cabaca("l", V_ml=3000.0, d_mm=40.0)
    assert c_small.f_H > c_large.f_H


def test_cabaca_larger_opening_higher_fH():
    c_narrow = Cabaca("n", V_ml=2000.0, d_mm=30.0)
    c_wide   = Cabaca("w", V_ml=2000.0, d_mm=70.0)
    assert c_wide.f_H > c_narrow.f_H


def test_cabaca_note_matches_freq_to_note():
    c = Cabaca("x", V_ml=2600.0, d_mm=60.0)
    assert c.note == freq_to_note(c.f_H)
