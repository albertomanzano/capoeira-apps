import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from views.cabacas import cabacas_view
from views.biribas import biribas_view

ACCENT  = "#f0a500"
BG      = "#0d0d0d"
SURFACE = "#1a1a1a"
MUTED   = "#666666"

TABS = ["Cabaça", "Biriba", "Casar"]


def _casar_placeholder() -> ft.Container:
    return ft.Container(
        content=ft.Text("Casar — en construcción", size=16, color=MUTED),
        alignment=ft.alignment.Alignment(0, 0),
        expand=True,
        bgcolor=BG,
    )


def instrumentos_view(page: ft.Page) -> ft.Container:
    sub_views = [cabacas_view(page), biribas_view(page), _casar_placeholder()]
    active = [0]

    content = ft.Container(content=sub_views[0], expand=True)
    tab_row = ft.Row(spacing=0, expand=True)

    def build_tabs():
        def make_tab(label, idx):
            is_active = idx == active[0]
            return ft.Container(
                content=ft.Text(
                    label, size=13,
                    color="#000000" if is_active else MUTED,
                    weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=ACCENT if is_active else SURFACE,
                padding=ft.padding.symmetric(vertical=11),
                on_click=lambda e, i=idx: switch(i),
                expand=True,
            )
        tab_row.controls = [make_tab(label, i) for i, label in enumerate(TABS)]

    def switch(idx):
        active[0] = idx
        content.content = sub_views[idx]
        build_tabs()
        page.update()

    build_tabs()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(content=tab_row, bgcolor=SURFACE),
                content,
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
        bgcolor=BG,
    )
