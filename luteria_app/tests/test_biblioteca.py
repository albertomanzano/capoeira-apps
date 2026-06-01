import json
import math
import pytest
import models.biblioteca as bib
from models.biriba import Biriba, WIRE_MU

# ── constantes START para tests ───────────────────────────────────────────────
_RHO = 7850
_MU_08 = _RHO * math.pi * (0.4e-3) ** 2
_MU_10 = _RHO * math.pi * (0.5e-3) ** 2


@pytest.fixture(autouse=True)
def isolated_json(tmp_path, monkeypatch):
    """Redirect _PATH to a temp file so each test starts with a blank library."""
    temp_file = tmp_path / "biblioteca.json"
    monkeypatch.setattr(bib, "_PATH", str(temp_file))


# ---------------------------------------------------------------------------
# add + get
# ---------------------------------------------------------------------------

def test_add_and_get_cabaca():
    bib.add_cabaca("Pequeña", 180.5, 350.0, 38.0)
    cabacas = bib.get_cabacas()
    assert len(cabacas) == 1
    c = cabacas[0]
    assert c["name"] == "Pequeña"
    assert c["f_H"] == pytest.approx(180.5, abs=0.01)
    assert c["V_ml"] == 350.0
    assert c["d_mm"] == 38.0


def test_add_and_get_biriba():
    bib.add_biriba("Biriba A", 3200.0, 115.0, 110.0, "0.9mm", 220.0)
    biribas = bib.get_biribas()
    assert len(biribas) == 1
    b = biribas[0]
    assert b["name"] == "Biriba A"
    assert b["k"] == pytest.approx(3200.0, abs=0.1)
    assert b["L0_cm"] == 115.0
    assert b["L_cm"] == 110.0
    assert b["calibre"] == "0.9mm"
    assert b["f1_measured"] == pytest.approx(220.0, abs=0.01)


def test_add_multiple_cabacas():
    bib.add_cabaca("Alpha", 100.0, 200.0, 30.0)
    bib.add_cabaca("Beta", 150.0, 250.0, 32.0)
    bib.add_cabaca("Gamma", 200.0, 300.0, 35.0)
    assert len(bib.get_cabacas()) == 3


def test_add_multiple_biribas():
    bib.add_biriba("B1", 3000.0, 110.0, 105.0, "0.8mm", 200.0)
    bib.add_biriba("B2", 3500.0, 120.0, 114.0, "1.0mm", 250.0)
    assert len(bib.get_biribas()) == 2


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

def test_update_cabaca_changes_fields():
    bib.add_cabaca("Original", 110.0, 300.0, 36.0)
    bib.update_cabaca(0, name="Modificada", f_H=125.5)
    c = bib.get_cabacas()[0]
    assert c["name"] == "Modificada"
    assert c["f_H"] == pytest.approx(125.5, abs=0.01)
    assert c["V_ml"] == 300.0   # campo no tocado permanece igual


def test_update_cabaca_does_not_affect_other_items():
    bib.add_cabaca("Primera", 100.0, 200.0, 30.0)
    bib.add_cabaca("Segunda", 200.0, 400.0, 40.0)
    bib.update_cabaca(0, name="Cambiada")
    cabacas = bib.get_cabacas()
    assert cabacas[0]["name"] == "Cambiada"
    assert cabacas[1]["name"] == "Segunda"


def test_update_biriba_changes_fields():
    bib.add_biriba("Original", 3000.0, 115.0, 110.0, "0.9mm", 220.0)
    bib.update_biriba(0, name="Actualizada", calibre="1.0mm")
    b = bib.get_biribas()[0]
    assert b["name"] == "Actualizada"
    assert b["calibre"] == "1.0mm"
    assert b["L0_cm"] == 115.0  # campo no tocado permanece igual


def test_update_biriba_does_not_affect_other_items():
    bib.add_biriba("B1", 3000.0, 110.0, 105.0, "0.8mm", 200.0)
    bib.add_biriba("B2", 3500.0, 120.0, 114.0, "1.0mm", 250.0)
    bib.update_biriba(1, name="B2 editada")
    biribas = bib.get_biribas()
    assert biribas[0]["name"] == "B1"
    assert biribas[1]["name"] == "B2 editada"


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def test_delete_cabaca_shrinks_list():
    bib.add_cabaca("A", 100.0, 200.0, 30.0)
    bib.add_cabaca("B", 150.0, 250.0, 32.0)
    bib.delete_cabaca(0)
    cabacas = bib.get_cabacas()
    assert len(cabacas) == 1
    assert cabacas[0]["name"] == "B"


def test_delete_biriba_shrinks_list():
    bib.add_biriba("B1", 3000.0, 110.0, 105.0, "0.8mm", 200.0)
    bib.add_biriba("B2", 3500.0, 120.0, 114.0, "1.0mm", 250.0)
    bib.delete_biriba(1)
    biribas = bib.get_biribas()
    assert len(biribas) == 1
    assert biribas[0]["name"] == "B1"


def test_delete_cabaca_middle_item():
    bib.add_cabaca("A", 100.0, 200.0, 30.0)
    bib.add_cabaca("B", 150.0, 250.0, 32.0)
    bib.add_cabaca("C", 200.0, 300.0, 35.0)
    bib.delete_cabaca(1)
    cabacas = bib.get_cabacas()
    assert len(cabacas) == 2
    assert cabacas[0]["name"] == "A"
    assert cabacas[1]["name"] == "C"


def test_delete_biriba_middle_item():
    bib.add_biriba("B1", 3000.0, 110.0, 105.0, "0.8mm", 200.0)
    bib.add_biriba("B2", 3500.0, 120.0, 114.0, "0.9mm", 220.0)
    bib.add_biriba("B3", 4000.0, 125.0, 118.0, "1.0mm", 260.0)
    bib.delete_biriba(1)
    biribas = bib.get_biribas()
    assert len(biribas) == 2
    assert biribas[0]["name"] == "B1"
    assert biribas[1]["name"] == "B3"


# ---------------------------------------------------------------------------
# persistencia: lo escrito en una llamada se lee en la siguiente
# ---------------------------------------------------------------------------

def test_persistence_cabaca_across_calls():
    bib.add_cabaca("Persistente", 180.0, 350.0, 38.0)
    # segunda llamada a _load() desde get_cabacas()
    result = bib.get_cabacas()
    assert result[0]["name"] == "Persistente"


def test_persistence_biriba_across_calls():
    bib.add_biriba("Persistente", 3200.0, 115.0, 110.0, "0.9mm", 220.0)
    result = bib.get_biribas()
    assert result[0]["name"] == "Persistente"


def test_persistence_update_survives_reload():
    bib.add_cabaca("Antes", 100.0, 200.0, 30.0)
    bib.update_cabaca(0, name="Despues")
    assert bib.get_cabacas()[0]["name"] == "Despues"


def test_persistence_delete_survives_reload():
    bib.add_cabaca("Efimera", 100.0, 200.0, 30.0)
    bib.add_cabaca("Duradera", 200.0, 400.0, 40.0)
    bib.delete_cabaca(0)
    assert bib.get_cabacas()[0]["name"] == "Duradera"


# ---------------------------------------------------------------------------
# integridad del JSON con múltiples ítems
# ---------------------------------------------------------------------------

def test_json_integrity_mixed_collections():
    bib.add_cabaca("C1", 100.0, 200.0, 30.0)
    bib.add_cabaca("C2", 200.0, 400.0, 40.0)
    bib.add_biriba("B1", 3000.0, 110.0, 105.0, "0.8mm", 200.0)
    bib.delete_cabaca(0)
    # biribas no se ven afectadas al borrar una cabaça
    assert len(bib.get_biribas()) == 1
    assert bib.get_biribas()[0]["name"] == "B1"
    assert len(bib.get_cabacas()) == 1
    assert bib.get_cabacas()[0]["name"] == "C2"


# ---------------------------------------------------------------------------
# edición: replica exactamente lo que hace el diálogo de la UI al guardar
# ---------------------------------------------------------------------------

def test_edit_cabaca_all_fields():
    """El diálogo envía name + f_H + V_ml + d_mm — todos deben persistir."""
    bib.add_cabaca("Original", 234.5, 2600.0, 60.0)
    bib.update_cabaca(0, name="Editada", f_H=240.0, V_ml=2800.0, d_mm=65.0)
    c = bib.get_cabacas()[0]
    assert c["name"] == "Editada"
    assert c["f_H"] == pytest.approx(240.0, abs=0.01)
    assert c["V_ml"] == pytest.approx(2800.0)
    assert c["d_mm"] == pytest.approx(65.0)


def test_edit_cabaca_preserves_date():
    """Editar no borra la fecha original."""
    bib.add_cabaca("C", 200.0, 1000.0, 50.0)
    original_date = bib.get_cabacas()[0]["date"]
    bib.update_cabaca(0, name="C editada", f_H=210.0)
    assert bib.get_cabacas()[0]["date"] == original_date


def test_edit_biriba_all_fields_k_recalculates():
    """El diálogo recalcula k a partir de los campos editados antes de guardar."""
    L0, L, cal, f1 = 148.0, 130.0, "0.9mm", 220.0
    bib.add_biriba("Original", 9000.0, L0, L, cal, f1)

    # Simula lo que hace do_save en el diálogo: recalcular k con nuevos valores
    new_L, new_f1 = 125.0, 240.0
    b = Biriba("", L0_cm=L0, L_cm=new_L, calibre=cal, f1_measured=new_f1)
    expected_k = round(b.k, 1)

    bib.update_biriba(0, name="Editada", k=expected_k,
                      L0_cm=L0, L_cm=new_L, calibre=cal, f1_measured=round(new_f1, 2))

    saved = bib.get_biribas()[0]
    assert saved["name"] == "Editada"
    assert saved["k"] == pytest.approx(expected_k, rel=1e-4)
    assert saved["L_cm"] == pytest.approx(new_L)
    assert saved["f1_measured"] == pytest.approx(new_f1, abs=0.01)


def test_edit_biriba_change_calibre_updates_k():
    """Cambiar el calibre con la misma posición produce una k diferente."""
    L0, L, f1 = 148.0, 130.0, 220.0
    b_thin  = Biriba("", L0_cm=L0, L_cm=L, calibre="0.7mm", f1_measured=f1)
    b_thick = Biriba("", L0_cm=L0, L_cm=L, calibre="1.0mm", f1_measured=f1)

    bib.add_biriba("Original", round(b_thin.k, 1), L0, L, "0.7mm", f1)
    bib.update_biriba(0, k=round(b_thick.k, 1), calibre="1.0mm")

    saved = bib.get_biribas()[0]
    assert saved["calibre"] == "1.0mm"
    assert saved["k"] == pytest.approx(b_thick.k, rel=1e-4)
    assert saved["k"] != pytest.approx(b_thin.k, rel=1e-4)


def test_edit_biriba_preserves_date():
    """Editar una biriba no borra la fecha original."""
    bib.add_biriba("B", 9000.0, 148.0, 130.0, "0.9mm", 220.0)
    original_date = bib.get_biribas()[0]["date"]
    bib.update_biriba(0, name="B editada", k=9500.0)
    assert bib.get_biribas()[0]["date"] == original_date


# ---------------------------------------------------------------------------
# arames — CRUD + defaults START
# ---------------------------------------------------------------------------

def test_defaults_loaded_on_first_get():
    """Sin arames guardados, get_arames() devuelve los dos START por defecto."""
    arames = bib.get_arames()
    assert len(arames) == 2
    names = [a['name'] for a in arames]
    assert 'START 0.8mm' in names
    assert 'START 1.0mm' in names


def test_defaults_mu_values():
    """μ de los arames START coincide con ρ=7850 kg/m³."""
    arames = {a['name']: a for a in bib.get_arames()}
    assert arames['START 0.8mm']['mu'] == pytest.approx(_MU_08, rel=1e-4)
    assert arames['START 1.0mm']['mu'] == pytest.approx(_MU_10, rel=1e-4)


def test_defaults_not_duplicated_on_second_call():
    """Llamar dos veces a get_arames() no duplica los defaults."""
    bib.get_arames()
    assert len(bib.get_arames()) == 2


def test_add_arame():
    bib.add_arame("Custom 0.9mm", "Artesanal", "0.9mm", _RHO * math.pi * (0.45e-3)**2)
    arames = bib.get_arames()
    custom = next(a for a in arames if a['name'] == "Custom 0.9mm")
    assert custom['brand'] == "Artesanal"
    assert custom['mu'] == pytest.approx(_RHO * math.pi * (0.45e-3)**2, rel=1e-4)


def test_update_arame():
    bib.get_arames()  # ensure defaults
    bib.update_arame(0, name="START 0.8mm editado", mu=round(_MU_08 * 1.01, 7))
    a = bib.get_arames()[0]
    assert a['name'] == "START 0.8mm editado"
    assert a['mu'] == pytest.approx(_MU_08 * 1.01, rel=1e-4)


def test_delete_arame():
    bib.get_arames()  # ensure defaults
    bib.delete_arame(0)
    remaining = bib.get_arames()
    # After delete, only one original default left (no re-seeding because list is non-empty)
    assert len(remaining) == 1
    assert remaining[0]['name'] == 'START 1.0mm'


def test_arame_mu_usable_in_biriba():
    """μ de un arame guardado permite construir un Biriba y calcular k correctamente."""
    arames = bib.get_arames()
    arame = next(a for a in arames if a['name'] == 'START 0.8mm')
    b = Biriba('', L0_cm=148, L_cm=130, mu=arame['mu'], f1_measured=220.0)
    expected_T = arame['mu'] * (2 * 1.30 * 220.0) ** 2
    expected_k = expected_T / (1.48 - 1.30)
    assert b.k == pytest.approx(expected_k, rel=1e-6)


def test_arame_fields_persisted():
    """Todos los campos de add_arame se guardan en el JSON."""
    bib.add_arame("Test wire", "TestBrand", "1.2mm", 8.5e-3, "Acero inox")
    a = next(x for x in bib.get_arames() if x['name'] == "Test wire")
    assert a['brand'] == "TestBrand"
    assert a['calibre'] == "1.2mm"
    assert a['mu'] == pytest.approx(8.5e-3, rel=1e-4)
    assert a['material'] == "Acero inox"
    assert 'date' in a


def test_json_valid_after_multiple_operations(tmp_path, monkeypatch):
    temp_file = tmp_path / "check.json"
    monkeypatch.setattr(bib, "_PATH", str(temp_file))

    bib.add_cabaca("X", 100.0, 200.0, 30.0)
    bib.add_cabaca("Y", 150.0, 250.0, 32.0)
    bib.add_cabaca("Z", 200.0, 300.0, 35.0)
    bib.update_cabaca(1, name="Y modificada")
    bib.delete_cabaca(1)

    with open(str(temp_file), encoding="utf-8") as f:
        data = json.load(f)

    assert "cabacas" in data
    assert "biribas" in data
    names = [c["name"] for c in data["cabacas"]]
    assert names == ["X", "Z"]
