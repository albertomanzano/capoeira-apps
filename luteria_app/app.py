import flet as ft
from views import instrumentos_view, biblioteca_view, herramientas_view


ACCENT  = "#f0a500"
BG      = "#0d0d0d"
SURFACE = "#1a1a1a"

BIBLIOTECA_IDX = 1


async def main(page: ft.Page):
    page.title = "Lutería"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.window.width = 390
    page.window.height = 844

    biblioteca_container, biblioteca_refresh = biblioteca_view(page)

    pages = [
        instrumentos_view(page),
        biblioteca_container,
        herramientas_view(page),
    ]

    content = ft.Container(content=pages[0], expand=True)

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == BIBLIOTECA_IDX:
            biblioteca_refresh()
        content.content = pages[idx]
        page.update()

    nav = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.QUEUE_MUSIC,   label="Instrumentos"),
            ft.NavigationBarDestination(icon=ft.Icons.LIBRARY_BOOKS, label="Biblioteca"),
            ft.NavigationBarDestination(icon=ft.Icons.TUNE,          label="Herramientas"),
        ],
        selected_index=0,
        bgcolor=SURFACE,
        indicator_color=ACCENT,
        on_change=on_nav_change,
    )

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[content, nav],
                expand=True,
                spacing=0,
            ),
            avoid_intrusions_bottom=False,
            expand=True,
        )
    )


ft.app(target=main)
