import math
import pytest
from models.biriba import Biriba, WIRE_MU


# ---------------------------------------------------------------------------
# Fixtures con valores concretos y verificables
# ---------------------------------------------------------------------------

# Biriba de referencia:
#   L0 = 115 cm, L = 110 cm, calibre 0.9mm, f1 medida = 220 Hz
#
# mu  = 7800 * pi * (0.45e-3)^2
# T   = mu * (2 * L * f1)^2
# k   = T / (L0 - L)

_L0_CM = 115.0
_L_CM  = 110.0
_CAL   = "0.9mm"
_F1    = 220.0


@pytest.fixture
def biriba():
    return Biriba("Ref", _L0_CM, _L_CM, _CAL, _F1)


def _expected_k(L0_cm, L_cm, calibre, f1):
    mu = WIRE_MU[calibre]
    L  = L_cm  * 1e-2
    L0 = L0_cm * 1e-2
    T  = mu * (2 * L * f1) ** 2
    return T / (L0 - L)


# ---------------------------------------------------------------------------
# Cálculo de k
# ---------------------------------------------------------------------------

def test_k_formula_reference(biriba):
    expected = _expected_k(_L0_CM, _L_CM, _CAL, _F1)
    assert biriba.k == pytest.approx(expected, rel=1e-6)


def test_k_formula_0_8mm():
    b = Biriba("B", 120.0, 114.0, "0.8mm", 200.0)
    expected = _expected_k(120.0, 114.0, "0.8mm", 200.0)
    assert b.k == pytest.approx(expected, rel=1e-6)


def test_k_formula_1_0mm():
    b = Biriba("B", 118.0, 112.0, "1.0mm", 260.0)
    expected = _expected_k(118.0, 112.0, "1.0mm", 260.0)
    assert b.k == pytest.approx(expected, rel=1e-6)


def test_k_is_positive(biriba):
    assert biriba.k > 0


def test_k_increases_with_stiffer_wire():
    """Mismas dimensiones y frecuencia medida: mayor calibre → mayor k."""
    b_thin  = Biriba("thin",  _L0_CM, _L_CM, "0.7mm", _F1)
    b_thick = Biriba("thick", _L0_CM, _L_CM, "1.0mm", _F1)
    assert b_thick.k > b_thin.k


# ---------------------------------------------------------------------------
# f1_at: reproducibilidad en L medida
# ---------------------------------------------------------------------------

def test_f1_at_reproduces_measured(biriba):
    L_m = _L_CM * 1e-2
    assert biriba.f1_at(L_m) == pytest.approx(_F1, rel=1e-6)


def test_f1_at_reproduces_measured_other_biriba():
    b = Biriba("B2", 120.0, 114.0, "0.8mm", 200.0)
    assert b.f1_at(114.0 * 1e-2) == pytest.approx(200.0, rel=1e-6)


# ---------------------------------------------------------------------------
# f1_at: borde T ≤ 0  (L ≥ L0)
# ---------------------------------------------------------------------------

def test_f1_at_returns_zero_when_L_equals_L0(biriba):
    assert biriba.f1_at(biriba.L0) == 0.0


def test_f1_at_returns_zero_when_L_exceeds_L0(biriba):
    assert biriba.f1_at(biriba.L0 + 0.01) == 0.0


def test_f1_at_returns_zero_well_above_L0(biriba):
    assert biriba.f1_at(biriba.L0 * 1.1) == 0.0


# ---------------------------------------------------------------------------
# f1_at: valores positivos dentro del rango físico
# ---------------------------------------------------------------------------

def test_f1_at_positive_below_L0(biriba):
    assert biriba.f1_at(biriba.L0 * 0.95) > 0.0


def test_f1_at_positive_at_min_extension(biriba):
    L_min = biriba.L0 * 0.80
    assert biriba.f1_at(L_min) > 0.0


# ---------------------------------------------------------------------------
# freq_range: dominio y valores
# ---------------------------------------------------------------------------

def test_freq_range_returns_300_points(biriba):
    L_vals, freqs = biriba.freq_range()
    assert len(L_vals) == 300
    assert len(freqs) == 300


def test_freq_range_L_vals_within_bounds(biriba):
    L_vals, _ = biriba.freq_range()
    assert L_vals.min() >= biriba.L0 * 0.80 - 1e-9
    assert L_vals.max() <= biriba.L0 * 0.995 + 1e-9


def test_freq_range_all_freqs_positive(biriba):
    _, freqs = biriba.freq_range()
    assert (freqs > 0).all(), "todas las frecuencias deben ser positivas dentro del rango"


def test_freq_range_custom_limits(biriba):
    L_min_cm = (_L0_CM * 0.90)
    L_max_cm = (_L0_CM * 0.98)
    L_vals, freqs = biriba.freq_range(L_min_cm=L_min_cm, L_max_cm=L_max_cm)
    assert L_vals.min() == pytest.approx(L_min_cm * 1e-2, rel=1e-6)
    assert L_vals.max() == pytest.approx(L_max_cm * 1e-2, rel=1e-6)
    assert (freqs > 0).all()


# ---------------------------------------------------------------------------
# Monotonía: más curvatura (L menor) → frecuencia mayor
# ---------------------------------------------------------------------------

def test_frequency_increases_as_L_decreases(biriba):
    """f1_at debe ser estrictamente decreciente al aumentar L (menos curvatura)."""
    L_vals, freqs = biriba.freq_range()
    # L_vals está en orden creciente (linspace), así que freqs debe ser decreciente
    diffs = freqs[1:] - freqs[:-1]
    assert (diffs < 0).all(), "f aumenta al disminuir L: freqs debe decrecer al aumentar L"


def test_shorter_L_gives_higher_freq(biriba):
    L_short = biriba.L0 * 0.85
    L_long  = biriba.L0 * 0.95
    assert biriba.f1_at(L_short) > biriba.f1_at(L_long)


def test_freq_range_max_at_smallest_L(biriba):
    L_vals, freqs = biriba.freq_range()
    assert freqs[0] == freqs.max()


def test_freq_range_min_at_largest_L(biriba):
    L_vals, freqs = biriba.freq_range()
    assert freqs[-1] == freqs.min()
