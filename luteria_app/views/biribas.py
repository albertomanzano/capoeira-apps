import asyncio
import concurrent.futures
import io
import os
import sys

import flet as ft
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.biriba import Biriba
from models.cabaca import freq_to_note
from models.biblioteca import add_biriba, get_arames

from audio.espectro import detect_f1, record_audio

ACCENT  = "#f0a500"
BG      = "#0d0d0d"
SURFACE = "#1a1a1a"
MUTED   = "#666666"

NOTE_PURE = {'Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Si'}

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def _notes_in_range(f_min: float, f_max: float) -> list[tuple[float, str]]:
    names = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
    result = []
    for midi in range(24, 108):
        f = 440.0 * 2 ** ((midi - 69) / 12)
        if f_min <= f <= f_max and names[midi % 12] in NOTE_PURE:
            result.append((f, f"{names[midi % 12]}{midi // 12 - 1}"))
    return result


def _plot_curve(biriba: Biriba) -> str:
    L_vals, freqs = biriba.freq_range()
    L_cm  = L_vals * 100
    valid = freqs > 0
    f_min = float(freqs[valid].min())
    f_max = float(freqs[valid].max())
    pad   = (f_max - f_min) * 0.06

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 3.8), facecolor='#0d0d0d')
    ax.set_facecolor('#111111')

    ax.plot(L_cm[valid], freqs[valid], color=ACCENT, linewidth=2.0)
    ax.scatter([biriba.L * 100], [biriba.f1_measured],
               color='white', s=55, zorder=5, label=f"{biriba.f1_measured:.0f} Hz")
    ax.set_ylim(f_min - pad, f_max + pad)

    note_data = _notes_in_range(f_min, f_max)
    if note_data:
        for f_note, _ in note_data:
            ax.axhline(f_note, color='#2a2a2a', linewidth=0.8, linestyle='--')
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.set_yticks([f for f, _ in note_data])
        ax2.set_yticklabels([n for _, n in note_data], fontsize=7)
        ax2.tick_params(colors='#666', labelsize=7, length=0)
        for spine in ax2.spines.values():
            spine.set_edgecolor('#333')

    ax.set_xlabel('L (cm)', color='#aaa', fontsize=9)
    ax.set_ylabel('f₁ (Hz)', color='#aaa', fontsize=9)
    ax.tick_params(colors='#666', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')
    ax.grid(True, color='#1a1a1a', linewidth=0.5)
    ax.legend(fontsize=7, labelcolor='white', framealpha=0.2,
              loc='upper right', markerscale=0.8)
    plt.tight_layout(pad=1.0)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, facecolor='#0d0d0d')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def biribas_view(page: ft.Page) -> ft.Container:
    L0_field = ft.TextField(
        label="L₀ (cm) — palo recto",
        hint_text="ej. 148",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        width=300,
    )
    L_field = ft.TextField(
        label="L (cm) — arame montado",
        hint_text="ej. 130",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        width=300,
    )

    # — Arame selector —
    arame_dd = ft.Dropdown(
        label="Arame",
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        expand=True,
    )
    mu_text = ft.Text("", size=11, color=MUTED)

    def _populate_arames():
        arames = get_arames()
        arame_dd.options = [ft.dropdown.Option(a['name']) for a in arames]
        if arames and not arame_dd.value:
            arame_dd.value = arames[0]['name']
        _update_mu_text()

    def _update_mu_text(e=None):
        arames = get_arames()
        selected = next((a for a in arames if a['name'] == arame_dd.value), None)
        mu_text.value = f"μ = {selected['mu']*1000:.2f} g/m" if selected else ""
        page.update()

    arame_dd.on_change = _update_mu_text

    _populate_arames()

    arame_row = ft.Row(
        controls=[
            arame_dd,
            ft.IconButton(
                icon=ft.Icons.REFRESH, icon_color=MUTED, icon_size=18,
                tooltip="Recargar arames",
                on_click=lambda e: (_populate_arames(), page.update()),
            ),
        ],
        width=300,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    status_text = ft.Text("", size=13, color=MUTED)
    error_text  = ft.Text("", size=13, color="#e57373")
    result_area = ft.Column([], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
    _current: dict = {}

    measure_btn = ft.ElevatedButton(
        content=ft.Text("Medir percusión", color="#000000", weight=ft.FontWeight.BOLD),
        bgcolor=ACCENT, width=300,
    )

    # — Save section —
    name_field    = ft.TextField(
        label="Nombre",
        hint_text='ej. "biriba mediana 2"',
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        expand=True,
    )
    save_feedback = ft.Text("", size=12, color="#81c784")
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

    def _do_save():
        name = (name_field.value or "").strip()
        if not name or not _current:
            save_feedback.value = "Escribe un nombre primero"
            save_feedback.color = "#e57373"
            page.update()
            return
        add_biriba(name, _current['k'], _current['L0_cm'], _current['L_cm'],
                   _current['calibre'], _current['f1_measured'],
                   mu=_current.get('mu'), arame_name=_current.get('arame_name'))
        name_field.value    = ""
        save_feedback.value = "✓ Guardado en biblioteca"
        save_feedback.color = "#81c784"
        page.update()

    async def do_measure():
        try:
            L0 = float(L0_field.value or "0")
            L  = float(L_field.value or "0")
            if L0 <= 0 or L <= 0 or L >= L0:
                raise ValueError
            error_text.value = ""
        except ValueError:
            error_text.value = "L₀ y L deben ser positivos, y L < L₀"
            page.update()
            return

        # Resolve selected arame
        arames = get_arames()
        selected_arame = next((a for a in arames if a['name'] == arame_dd.value), None)
        if selected_arame is None:
            error_text.value = "Selecciona un arame"
            page.update()
            return

        measure_btn.disabled = True
        status_text.value = "Grabando 3 segundos..."
        status_text.color = ACCENT
        page.update()

        try:
            loop  = asyncio.get_event_loop()
            audio = await loop.run_in_executor(_executor, record_audio)

            status_text.value = "Detectando f₁..."
            page.update()

            f1 = await loop.run_in_executor(_executor, detect_f1, audio)

            if f1 is None:
                error_text.value = "No se detectó señal. Percute el arame e intenta de nuevo."
                status_text.value = ""
                measure_btn.disabled = False
                page.update()
                return

            biriba = Biriba("", L0_cm=L0, L_cm=L,
                            calibre=selected_arame.get('calibre') or None,
                            f1_measured=f1,
                            mu=selected_arame['mu'])

            status_text.value = "Calculando curva..."
            page.update()

            b64 = await loop.run_in_executor(_executor, _plot_curve, biriba)

            _, freqs_curve = biriba.freq_range()
            valid = freqs_curve > 0
            f_lo    = float(freqs_curve[valid].min())
            f_hi    = float(freqs_curve[valid].max())
            note_lo = freq_to_note(f_lo).split('(')[0].strip()
            note_hi = freq_to_note(f_hi).split('(')[0].strip()
            note_f1 = freq_to_note(f1).split('(')[0].strip()

            _current.update({
                'k': biriba.k, 'L0_cm': L0, 'L_cm': L,
                'calibre': selected_arame.get('calibre', ''),
                'f1_measured': f1,
                'mu': selected_arame['mu'],
                'arame_name': selected_arame['name'],
            })
            save_feedback.value = ""

            result_area.controls = [
                ft.Divider(color=SURFACE),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("k", size=11, color=MUTED),
                                ft.Text(f"{biriba.k:.0f} N/m", size=26, color=ACCENT,
                                        weight=ft.FontWeight.BOLD),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.VerticalDivider(color=SURFACE, width=1),
                        ft.Column(
                            controls=[
                                ft.Text("f₁ medida", size=11, color=MUTED),
                                ft.Text(f"{f1:.1f} Hz", size=26, color="white",
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(note_f1, size=13, color=MUTED),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.VerticalDivider(color=SURFACE, width=1),
                        ft.Column(
                            controls=[
                                ft.Text("rango", size=11, color=MUTED),
                                ft.Text(f"{note_lo} – {note_hi}", size=18, color="white",
                                        weight=ft.FontWeight.BOLD),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=28,
                ),
                ft.Container(height=4),
                ft.Image(src=b64, width=660, fit=ft.BoxFit.CONTAIN),
                ft.Container(height=4),
                save_row,
                save_feedback,
            ]

            status_text.value = "Listo."
            status_text.color = MUTED
        except Exception as exc:
            error_text.value = f"Error: {exc}"
            status_text.value = ""
        finally:
            measure_btn.disabled = False
        page.update()

    measure_btn.on_click = lambda e: page.run_task(do_measure)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Biriba", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Caracteriza una biriba midiendo k", size=13, color=MUTED),
                ft.Container(height=8),
                L0_field,
                L_field,
                arame_row,
                mu_text,
                error_text,
                measure_btn,
                status_text,
                ft.Container(height=4),
                result_area,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
        alignment=ft.alignment.Alignment(0, -0.1),
        expand=True,
        bgcolor=BG,
        padding=24,
    )
