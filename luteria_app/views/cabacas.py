import asyncio
import concurrent.futures
import math
import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models import Cabaca
from models.cabaca import freq_to_note
from models.biblioteca import add_cabaca

ACCENT  = "#f0a500"
BG      = "#0d0d0d"
SURFACE = "#1a1a1a"
MUTED   = "#666666"

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def cabacas_view(page: ft.Page) -> ft.Container:
    # ── sección calcular ─────────────────────────────────────────────────────
    v_field = ft.TextField(
        label="Volumen V (ml)",
        hint_text="ej. 2600",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        width=300,
    )
    d_field = ft.TextField(
        label="Diámetro boca d (mm)",
        hint_text="ej. 60",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        width=300,
    )

    fH_text    = ft.Text("", size=32, color=ACCENT, weight=ft.FontWeight.BOLD)
    note_text  = ft.Text("", size=18, color="white")
    error_text = ft.Text("", size=13, color="#e57373")

    name_field = ft.TextField(
        label="Nombre",
        hint_text='ej. "cabaça grande 1"',
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        expand=True,
    )
    save_feedback = ft.Text("", size=12, color="#81c784")
    _current: dict = {}

    def _do_save():
        name = (name_field.value or "").strip()
        if not name or not _current:
            save_feedback.value = "Escribe un nombre primero"
            save_feedback.color = "#e57373"
            page.update()
            return
        add_cabaca(name, _current['f_H'], _current['V_ml'], _current['d_mm'])
        name_field.value    = ""
        save_feedback.value = "✓ Guardado en biblioteca"
        save_feedback.color = "#81c784"
        page.update()

    save_row = ft.Row(
        controls=[
            name_field,
            ft.ElevatedButton(
                content=ft.Text("Guardar", color="#000000", weight=ft.FontWeight.BOLD),
                bgcolor=ACCENT,
                on_click=lambda e: _do_save(),
                height=56,
            ),
        ],
        width=340,
    )

    result_col = ft.Column(
        controls=[
            ft.Divider(color=SURFACE),
            fH_text,
            note_text,
            ft.Container(height=4),
            save_row,
            save_feedback,
        ],
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
    )

    def calculate(e):
        error_text.value = ""
        save_feedback.value = ""
        try:
            V = float(v_field.value or "0")
            d = float(d_field.value or "0")
            if V <= 0 or d <= 0:
                raise ValueError
            c = Cabaca("", V_ml=V, d_mm=d)
            fH_text.value   = f"{c.f_H:.1f} Hz"
            note_text.value = c.note
            _current.update({'f_H': c.f_H, 'V_ml': V, 'd_mm': d})
            result_col.visible = True
        except ValueError:
            result_col.visible = False
            error_text.value   = "Introduce valores válidos"
        page.update()

    # ── sección medir ─────────────────────────────────────────────────────────
    medir_status   = ft.Text("", size=12, color=MUTED)
    medir_fH_text  = ft.Text("", size=32, color="#4fc3f7", weight=ft.FontWeight.BOLD)
    medir_note_text = ft.Text("", size=18, color="white")
    medir_cmp_text  = ft.Text("", size=12, color=MUTED)

    medir_name_field = ft.TextField(
        label="Nombre",
        hint_text='ej. "cabaça grande 1"',
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        expand=True,
    )
    medir_save_feedback = ft.Text("", size=12, color="#81c784")
    _medir_current: dict = {}

    def _do_medir_save():
        name = (medir_name_field.value or "").strip()
        if not name or not _medir_current:
            medir_save_feedback.value = "Escribe un nombre primero"
            medir_save_feedback.color = "#e57373"
            page.update()
            return
        add_cabaca(name, _medir_current['f_H'],
                   _medir_current['V_ml'], _medir_current['d_mm'])
        medir_name_field.value      = ""
        medir_save_feedback.value   = "✓ Guardado en biblioteca"
        medir_save_feedback.color   = "#81c784"
        page.update()

    medir_save_row = ft.Row(
        controls=[
            medir_name_field,
            ft.ElevatedButton(
                content=ft.Text("Guardar", color="#000000", weight=ft.FontWeight.BOLD),
                bgcolor=ACCENT,
                on_click=lambda e: _do_medir_save(),
                height=56,
            ),
        ],
        width=340,
    )

    medir_result_col = ft.Column(
        controls=[
            medir_fH_text,
            medir_note_text,
            medir_cmp_text,
            ft.Container(height=4),
            medir_save_row,
            medir_save_feedback,
        ],
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
    )

    medir_btn = ft.ElevatedButton(
        content=ft.Text("Medir resonancia", color="#000000", weight=ft.FontWeight.BOLD),
        bgcolor=ACCENT,
        width=300,
    )

    _running = [False]

    async def do_measure():
        from audio.cabaca_search import (
            sweep_h1_once, accumulate, finalize,
            find_candidates, zoom_winner,
            N_BROAD, N_ZOOM, ZOOM_HZ,
            CHIRP_BROAD_DUR, CHIRP_ZOOM_DUR, WARMUP, F_MIN, F_MAX,
        )
        from audio.tono import generate_chirp

        _running[0] = True
        medir_btn.content = ft.Text("Detener", color="white", weight=ft.FontWeight.BOLD)
        medir_btn.bgcolor = "#e57373"
        medir_result_col.visible    = False
        medir_save_feedback.value   = ""
        page.update()

        loop = asyncio.get_event_loop()
        try:
            chirp_broad = generate_chirp(F_MIN, F_MAX, WARMUP + CHIRP_BROAD_DUR)
            acc, freqs = None, None

            for i in range(N_BROAD):
                if not _running[0]:
                    return
                medir_status.value = f"Barrido amplio {i+1}/{N_BROAD}..."
                medir_status.color = ACCENT
                page.update()
                Sxy, Sxx, Syy, freqs = await loop.run_in_executor(
                    _executor, sweep_h1_once, chirp_broad)
                acc = accumulate(acc, Sxy, Sxx, Syy)
                await asyncio.sleep(0.3)

            H1, coh, freqs = finalize(acc, freqs)
            candidates = find_candidates(H1, coh, freqs, F_MIN, F_MAX)

            zoom_results = []
            for ci, f_c in enumerate(candidates):
                fz_min = max(F_MIN, f_c - ZOOM_HZ)
                fz_max = min(F_MAX, f_c + ZOOM_HZ)
                chirp_z = generate_chirp(fz_min, fz_max, WARMUP + CHIRP_ZOOM_DUR)
                acc_z, freqs_z = None, None

                for i in range(N_ZOOM):
                    if not _running[0]:
                        return
                    medir_status.value = (
                        f"Afinando zona {ci+1}/{len(candidates)} — {i+1}/{N_ZOOM}..."
                    )
                    page.update()
                    Sxy, Sxx, Syy, freqs_z = await loop.run_in_executor(
                        _executor, sweep_h1_once, chirp_z)
                    acc_z = accumulate(acc_z, Sxy, Sxx, Syy)
                    await asyncio.sleep(0.3)

                H1z, cohz, freqs_z = finalize(acc_z, freqs_z)
                f_ref, c_ref = zoom_winner(H1z, cohz, freqs_z, fz_min, fz_max)
                zoom_results.append((f_ref, c_ref))

            winner_idx = max(range(len(zoom_results)), key=lambda i: zoom_results[i][1])
            f_H = zoom_results[winner_idx][0]

            V_ml = float(v_field.value or "0") or 0.0
            d_mm = float(d_field.value or "0") or 0.0
            _medir_current.update({'f_H': f_H, 'V_ml': V_ml, 'd_mm': d_mm})

            medir_fH_text.value  = f"{f_H:.1f} Hz"
            medir_note_text.value = freq_to_note(f_H)

            if _current.get('f_H'):
                cents = round(1200 * math.log2(f_H / _current['f_H']))
                sign  = '+' if cents >= 0 else ''
                medir_cmp_text.value = f"vs. estimación: {sign}{cents}c"
            else:
                medir_cmp_text.value = ""

            medir_result_col.visible = True
            medir_status.value = "Medición completa"
            medir_status.color = "#81c784"

        except Exception as exc:
            medir_status.value = f"Error: {exc}"
            medir_status.color = "#e57373"
        finally:
            _running[0] = False
            medir_btn.content = ft.Text("Medir resonancia", color="#000000",
                                        weight=ft.FontWeight.BOLD)
            medir_btn.bgcolor = ACCENT
            page.update()

    def on_medir(e):
        if _running[0]:
            _running[0] = False
        else:
            page.run_task(do_measure)

    medir_btn.on_click = on_medir

    # ── layout ────────────────────────────────────────────────────────────────
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Cabaça", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Estimación por dimensiones", size=13, color=MUTED),
                ft.Container(height=8),
                v_field,
                d_field,
                error_text,
                ft.ElevatedButton(
                    content=ft.Text("Calcular", color="#000000", weight=ft.FontWeight.BOLD),
                    bgcolor=ACCENT,
                    on_click=calculate,
                    width=300,
                ),
                result_col,
                ft.Divider(color=SURFACE),
                ft.Text("Medir resonancia", size=18, weight=ft.FontWeight.BOLD,
                        color="white"),
                ft.Text(
                    "Apunta el altavoz hacia la boca de la cabaça (~5 cm).\n"
                    "El micrófono grabará la resonancia.",
                    size=12, color=MUTED,
                ),
                ft.Container(height=4),
                medir_btn,
                medir_status,
                medir_result_col,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
        alignment=ft.alignment.Alignment(0, -0.3),
        expand=True,
        bgcolor=BG,
        padding=24,
    )
