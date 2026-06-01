import asyncio
import concurrent.futures
import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from audio.espectro import (GROUP_COLORS, process_and_plot, record_audio,
                             scale_color)
from audio.android_audio import MicPermissionError, open_app_settings

ACCENT  = "#f0a500"
BG      = "#0d0d0d"
SURFACE = "#1a1a1a"
MUTED   = "#666666"

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def _fundamental_card(groups) -> ft.Container:
    """Tarjeta con el tono fundamental del grupo dominante."""
    from models.cabaca import freq_to_note
    if not groups:
        return ft.Container()
    dominant = groups[0]
    f, _, n  = min(dominant, key=lambda x: x[2])
    f0       = f / n
    note     = freq_to_note(f0).split('(')[0].strip()
    color    = GROUP_COLORS[0]
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("TONO FUNDAMENTAL", size=10, color=MUTED,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(note, size=48, color=color,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(f"{f0:.1f} Hz", size=16, color="white"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE,
        border_radius=12,
        padding=ft.padding.symmetric(vertical=16, horizontal=32),
    )


def _format_peaks_text(groups, ungrouped, group_share, peak_share, noise_share):
    from models.cabaca import freq_to_note
    series_cols = []
    for gi, (group, g_share) in enumerate(zip(groups, group_share)):
        color  = GROUP_COLORS[gi % len(GROUP_COLORS)]
        header = ft.Text(
            f"Serie {gi+1}  —  {g_share*100:.0f}%",
            color=color, size=13, weight=ft.FontWeight.BOLD,
        )
        rows = []
        for (f, amp, n), p_share in zip(sorted(group, key=lambda x: x[2]), peak_share[gi]):
            note = freq_to_note(f).split('(')[0].strip()
            rows.append(ft.Text(
                f"n={n}  {note}  {f:.0f} Hz\n{p_share*100:.0f}% de la serie",
                color=scale_color(color, 0.6 + 0.4 * p_share),
                size=12,
            ))
        series_cols.append(
            ft.Container(
                content=ft.Column([header, *rows], spacing=4),
                padding=ft.padding.only(right=24),
            )
        )
    return [ft.Row(series_cols, vertical_alignment=ft.CrossAxisAlignment.START, wrap=True)]


def espectro_view(page: ft.Page) -> ft.Container:
    status_text = ft.Text("Pulsa grabar para capturar 3 segundos de audio.",
                          size=13, color=MUTED)
    result_area = ft.Column([], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6)
    record_btn  = ft.ElevatedButton(
        content=ft.Text("Grabar", color="#000000", weight=ft.FontWeight.BOLD),
        bgcolor=ACCENT, width=200,
    )
    async def do_record():
        record_btn.disabled = True
        status_text.value   = "Grabando..."
        status_text.color   = ACCENT
        page.update()

        try:
            loop  = asyncio.get_event_loop()
            audio = await loop.run_in_executor(_executor, record_audio)

            status_text.value = "Procesando..."
            page.update()

            groups, ungrouped, group_share, peak_share, noise_share, b64 = \
                await loop.run_in_executor(_executor, process_and_plot, audio)

            total_amp = sum(a for g in groups for _, a, _ in g)
            if not groups or total_amp == 0:
                status_text.value = "No se detectó señal. Percute el instrumento e intenta de nuevo."
                status_text.color = "#e57373"
                record_btn.disabled = False
                page.update()
                return

            result_area.controls = [
                _fundamental_card(groups),
                ft.Container(height=8),
                ft.Image(src=b64, width=660, fit=ft.BoxFit.CONTAIN),
                ft.Container(height=4),
                *_format_peaks_text(groups, ungrouped, group_share, peak_share, noise_share),
            ]
            status_text.value   = "Listo."
            status_text.color   = MUTED
        except MicPermissionError:
            status_text.value = "Permiso de micrófono no concedido."
            status_text.color = "#e57373"
            result_area.controls = [
                ft.ElevatedButton(
                    content=ft.Text("Abrir ajustes de permisos", color="#000000",
                                    weight=ft.FontWeight.BOLD),
                    bgcolor=ACCENT,
                    on_click=lambda e: open_app_settings(),
                )
            ]
        except Exception as exc:
            status_text.value = f"Error: {exc}"
            status_text.color = "#e57373"
        finally:
            record_btn.disabled = False
        page.update()

    record_btn.on_click = lambda e: page.run_task(do_record)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Analizador de espectro", size=24,
                        weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Captura 3 segundos del micrófono", size=13, color=MUTED),
                ft.Container(height=8),
                record_btn,
                status_text,
                ft.Container(height=4),
                result_area,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
        alignment=ft.alignment.Alignment(0, -0.1),
        expand=True,
        bgcolor=BG,
        padding=24,
    )
