import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.biblioteca import (delete_cabaca, delete_biriba, delete_arame,
                                get_cabacas, get_biribas, get_arames,
                                update_cabaca, update_biriba, update_arame,
                                add_arame)
from models.biriba import Biriba
from models.cabaca import freq_to_note

ACCENT  = "#f0a500"
BG      = "#0d0d0d"
SURFACE = "#1a1a1a"
MUTED   = "#666666"
CALIBRES = ['0.7mm', '0.8mm', '0.9mm', '1.0mm']


def _tf(label, value, numeric=False, width=None):
    kw = dict(
        label=label, value=str(value),
        filled=True, fill_color="#222222",
        border_color=MUTED, focused_border_color=ACCENT,
    )
    if numeric:
        kw['keyboard_type'] = ft.KeyboardType.NUMBER
    if width:
        kw['width'] = width
    return ft.TextField(**kw)


def _biriba_range(entry: dict) -> str:
    b = Biriba('', L0_cm=entry['L0_cm'], L_cm=entry['L_cm'],
               calibre=entry.get('calibre') or None,
               f1_measured=entry['f1_measured'],
               mu=entry.get('mu'))
    _, freqs = b.freq_range()
    valid = freqs > 0
    lo = freq_to_note(float(freqs[valid].min())).split('(')[0].strip()
    hi = freq_to_note(float(freqs[valid].max())).split('(')[0].strip()
    return f"{lo} – {hi}"


# ── edit dialogs ──────────────────────────────────────────────────────────────

def _edit_cabaca_dialog(page, idx, entry, on_saved):
    name_f = _tf("Nombre", entry['name'])
    fH_f   = _tf("f_H (Hz)", entry['f_H'], numeric=True)
    v_f    = _tf("Volumen V (ml)", entry.get('V_ml', ''), numeric=True)
    d_f    = _tf("Diámetro d (mm)", entry.get('d_mm', ''), numeric=True)
    err_t  = ft.Text("", color="#e57373", size=12)

    def do_save(e):
        try:
            name = name_f.value.strip()
            fH   = float(fH_f.value)
            V    = float(v_f.value) if v_f.value.strip() else entry.get('V_ml', 0)
            d    = float(d_f.value) if d_f.value.strip() else entry.get('d_mm', 0)
            if not name or fH <= 0:
                raise ValueError
        except ValueError:
            err_t.value = "Valores no válidos"
            page.update()
            return
        update_cabaca(idx, name=name, f_H=round(fH, 2), V_ml=V, d_mm=d)
        dlg.open = False
        on_saved()
        page.update()

    def do_cancel(e):
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Editar cabaça", color="white"),
        content=ft.Column(
            [name_f, fH_f, v_f, d_f, err_t],
            tight=True, spacing=10, width=300,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=do_cancel),
            ft.ElevatedButton(
                content=ft.Text("Guardar", color="#000000", weight=ft.FontWeight.BOLD),
                bgcolor=ACCENT, on_click=do_save,
            ),
        ],
        bgcolor=SURFACE,
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.AlertDialog)]
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def _edit_biriba_dialog(page, idx, entry, on_saved):
    name_f  = _tf("Nombre", entry['name'])
    L0_f    = _tf("L₀ (cm)", entry['L0_cm'], numeric=True)
    L_f     = _tf("L (cm)", entry['L_cm'], numeric=True)
    cal_dd  = ft.Dropdown(
        label="Calibre",
        options=[ft.dropdown.Option(c) for c in CALIBRES],
        value=entry['calibre'],
        filled=True, fill_color="#222222",
        border_color=MUTED, focused_border_color=ACCENT,
    )
    f1_f    = _tf("f₁ medida (Hz)", entry['f1_measured'], numeric=True)
    err_t   = ft.Text("", color="#e57373", size=12)

    def do_save(e):
        try:
            name = name_f.value.strip()
            L0   = float(L0_f.value)
            L    = float(L_f.value)
            cal  = cal_dd.value
            f1   = float(f1_f.value)
            if not name or L0 <= 0 or L <= 0 or L >= L0 or f1 <= 0:
                raise ValueError
        except ValueError:
            err_t.value = "Valores no válidos"
            page.update()
            return
        b = Biriba('', L0_cm=L0, L_cm=L, calibre=cal, f1_measured=f1)
        update_biriba(idx, name=name, k=round(b.k, 1),
                      L0_cm=L0, L_cm=L, calibre=cal, f1_measured=round(f1, 2))
        dlg.open = False
        on_saved()
        page.update()

    def do_cancel(e):
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Editar biriba", color="white"),
        content=ft.Column(
            [name_f, L0_f, L_f, cal_dd, f1_f, err_t],
            tight=True, spacing=10, width=300,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=do_cancel),
            ft.ElevatedButton(
                content=ft.Text("Guardar", color="#000000", weight=ft.FontWeight.BOLD),
                bgcolor=ACCENT, on_click=do_save,
            ),
        ],
        bgcolor=SURFACE,
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.AlertDialog)]
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


# ── item cards ────────────────────────────────────────────────────────────────

def _cabaca_card(entry, idx, page, on_change) -> ft.Container:
    note = freq_to_note(entry['f_H']).split('(')[0].strip()
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(entry['name'], size=14, color="white",
                                weight=ft.FontWeight.W_500),
                        ft.Text(f"{entry['f_H']:.1f} Hz  ·  {note}  ·  {entry['date']}",
                                size=11, color=MUTED),
                    ],
                    spacing=2, expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED, icon_color=MUTED, icon_size=18,
                    tooltip="Editar",
                    on_click=lambda e, i=idx, en=entry: _edit_cabaca_dialog(
                        page, i, en, on_change),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE, icon_color=MUTED, icon_size=18,
                    tooltip="Eliminar",
                    on_click=lambda e, i=idx: (_do_delete_cabaca(i, on_change, page)),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE, border_radius=8,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
    )


def _biriba_card(entry, idx, page, on_change) -> ft.Container:
    rng = _biriba_range(entry)
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(entry['name'], size=14, color="white",
                                weight=ft.FontWeight.W_500),
                        ft.Text(
                            f"k={entry['k']:.0f} N/m  ·  {rng}"
                            f"  ·  {entry['calibre']}  ·  {entry['date']}",
                            size=11, color=MUTED,
                        ),
                    ],
                    spacing=2, expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED, icon_color=MUTED, icon_size=18,
                    tooltip="Editar",
                    on_click=lambda e, i=idx, en=entry: _edit_biriba_dialog(
                        page, i, en, on_change),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE, icon_color=MUTED, icon_size=18,
                    tooltip="Eliminar",
                    on_click=lambda e, i=idx: _do_delete_biriba(i, on_change, page),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE, border_radius=8,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
    )


def _do_delete_cabaca(idx, on_change, page):
    delete_cabaca(idx)
    on_change()
    page.update()


def _do_delete_biriba(idx, on_change, page):
    delete_biriba(idx)
    on_change()
    page.update()


def _do_delete_arame(idx, on_change, page):
    delete_arame(idx)
    on_change()
    page.update()


# ── arame edit dialog ─────────────────────────────────────────────────────────

def _edit_arame_dialog(page, idx, entry, on_saved):
    name_f  = _tf("Nombre", entry['name'])
    brand_f = _tf("Marca", entry.get('brand', ''))
    cal_f   = _tf("Calibre", entry.get('calibre', ''))
    mu_f    = _tf("μ (g/m)", f"{entry['mu']*1000:.3f}", numeric=True)
    mat_f   = _tf("Material", entry.get('material', ''))
    err_t   = ft.Text("", color="#e57373", size=12)

    def do_save(e):
        try:
            name  = name_f.value.strip()
            brand = brand_f.value.strip()
            cal   = cal_f.value.strip()
            mu_gm = float(mu_f.value)
            mat   = mat_f.value.strip()
            if not name or mu_gm <= 0:
                raise ValueError
        except ValueError:
            err_t.value = "Nombre y μ son obligatorios"
            page.update()
            return
        update_arame(idx, name=name, brand=brand, calibre=cal,
                     mu=round(mu_gm / 1000, 7), material=mat)
        dlg.open = False
        on_saved()
        page.update()

    def do_cancel(e):
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Editar arame", color="white"),
        content=ft.Column(
            [name_f, brand_f, cal_f, mu_f, mat_f, err_t],
            tight=True, spacing=10, width=300,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=do_cancel),
            ft.ElevatedButton(
                content=ft.Text("Guardar", color="#000000", weight=ft.FontWeight.BOLD),
                bgcolor=ACCENT, on_click=do_save,
            ),
        ],
        bgcolor=SURFACE,
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.AlertDialog)]
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def _arame_card(entry, idx, page, on_change) -> ft.Container:
    mu_gm = entry['mu'] * 1000
    label = f"μ={mu_gm:.2f} g/m  ·  {entry.get('calibre','')}  ·  {entry.get('material','')}"
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(entry['name'], size=14, color="white",
                                weight=ft.FontWeight.W_500),
                        ft.Text(label.strip('  ·  '), size=11, color=MUTED),
                    ],
                    spacing=2, expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED, icon_color=MUTED, icon_size=18,
                    tooltip="Editar",
                    on_click=lambda e, i=idx, en=entry: _edit_arame_dialog(
                        page, i, en, on_change),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE, icon_color=MUTED, icon_size=18,
                    tooltip="Eliminar",
                    on_click=lambda e, i=idx: _do_delete_arame(i, on_change, page),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE, border_radius=8,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
    )


# ── main view ─────────────────────────────────────────────────────────────────

def biblioteca_view(page: ft.Page) -> tuple:
    """Returns (container, refresh_fn). Call refresh_fn() when navigating to this tab."""
    cabacas_col = ft.Column([], spacing=6)
    biribas_col = ft.Column([], spacing=6)
    arames_col  = ft.Column([], spacing=6)

    def refresh():
        cabacas = get_cabacas()
        biribas = get_biribas()
        arames  = get_arames()

        cabacas_col.controls = (
            [_cabaca_card(e, i, page, refresh) for i, e in enumerate(cabacas)]
            if cabacas else [ft.Text("Vacío", size=13, color=MUTED)]
        )
        biribas_col.controls = (
            [_biriba_card(e, i, page, refresh) for i, e in enumerate(biribas)]
            if biribas else [ft.Text("Vacío", size=13, color=MUTED)]
        )
        arames_col.controls = (
            [_arame_card(e, i, page, refresh) for i, e in enumerate(arames)]
            if arames else [ft.Text("Vacío", size=13, color=MUTED)]
        )
        page.update()

    refresh()

    container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Biblioteca", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=8),
                ft.Text("ARAMES", size=11, color=MUTED, weight=ft.FontWeight.BOLD),
                ft.Container(height=2),
                arames_col,
                ft.Container(height=12),
                ft.Text("CABAÇAS", size=11, color=MUTED, weight=ft.FontWeight.BOLD),
                ft.Container(height=2),
                cabacas_col,
                ft.Container(height=12),
                ft.Text("BIRIBAS", size=11, color=MUTED, weight=ft.FontWeight.BOLD),
                ft.Container(height=2),
                biribas_col,
            ],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
        ),
        alignment=ft.alignment.Alignment(0, -1),
        expand=True,
        bgcolor=BG,
        padding=24,
    )
    return container, refresh
