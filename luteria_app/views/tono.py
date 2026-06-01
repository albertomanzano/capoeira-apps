import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from audio.tono import TonePlayer
from models.cabaca import freq_to_note

ACCENT  = "#f0a500"
BG      = "#0d0d0d"
SURFACE = "#1a1a1a"
MUTED   = "#666666"

F_MIN, F_MAX = 50, 1000


def tono_view(page: ft.Page) -> ft.Container:
    player = TonePlayer()

    freq_display = ft.Text("440 Hz", size=36, color=ACCENT, weight=ft.FontWeight.BOLD)
    note_display = ft.Text(freq_to_note(440), size=18, color="white")

    slider = ft.Slider(
        value=440, min=F_MIN, max=F_MAX, divisions=950,
        active_color=ACCENT, thumb_color=ACCENT,
        width=320,
    )

    freq_field = ft.TextField(
        value="440",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True, fill_color=SURFACE,
        border_color=MUTED, focused_border_color=ACCENT,
        width=120, text_align=ft.TextAlign.CENTER,
        suffix=ft.Text("Hz", color=MUTED),
    )

    play_btn = ft.ElevatedButton(
        content=ft.Text("Reproducir", color="#000000", weight=ft.FontWeight.BOLD),
        bgcolor=ACCENT, width=200,
    )

    def update_displays(freq: float):
        freq_display.value = f"{freq:.1f} Hz"
        note_display.value = freq_to_note(freq)

    def on_slider_change(e):
        freq = round(e.control.value, 1)
        freq_field.value = str(int(freq))
        update_displays(freq)
        if player.stream:
            player.set_freq(freq)
        page.update()

    def on_field_submit(e):
        try:
            freq = float(freq_field.value)
            freq = max(F_MIN, min(F_MAX, freq))
            slider.value = freq
            freq_field.value = str(int(freq))
            update_displays(freq)
            if player.stream:
                player.set_freq(freq)
        except ValueError:
            pass
        page.update()

    def on_play_stop(e):
        if player.stream:
            player.stop()
            play_btn.content = ft.Text("Reproducir", color="#000000", weight=ft.FontWeight.BOLD)
            play_btn.bgcolor = ACCENT
        else:
            player.start(slider.value)
            play_btn.content = ft.Text("Detener", color="white", weight=ft.FontWeight.BOLD)
            play_btn.bgcolor = "#e57373"
        page.update()

    slider.on_change   = on_slider_change
    freq_field.on_submit = on_field_submit
    play_btn.on_click  = on_play_stop

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Generador de tono", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Tono sinusoidal puro", size=13, color=MUTED),
                ft.Container(height=16),
                freq_display,
                note_display,
                ft.Container(height=8),
                slider,
                ft.Row(
                    controls=[
                        ft.Text("Frecuencia exacta:", color=MUTED, size=13),
                        freq_field,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                ),
                ft.Container(height=8),
                play_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.alignment.Alignment(0, -0.3),
        expand=True,
        bgcolor=BG,
        padding=24,
    )
