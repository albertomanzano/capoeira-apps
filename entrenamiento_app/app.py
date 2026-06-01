import flet as ft
from data import supabase as sb
from views.login    import build_login
from views.alumnos  import build_alumnos
from views.rutinas  import build_rutinas
from views.entrenar import build_entrenar
from views.historial import build_historial
from views.timer    import build_timer

BG   = "#0f0f0f"
CARD = "#1a1a1a"

async def main(page: ft.Page):
    page.title       = "Entrenamiento"
    page.theme_mode  = ft.ThemeMode.DARK
    page.bgcolor     = BG
    page.padding     = 0

    role = [None]

    content = ft.Container(
        expand=True,
        padding=ft.Padding(left=16, right=16, top=16, bottom=8),
        bgcolor=BG,
    )

    def _profe_nav():
        return [
            ft.NavigationBarDestination(icon=ft.Icons.PEOPLE_OUTLINE,     selected_icon=ft.Icons.PEOPLE,   label="Alumnos"),
            ft.NavigationBarDestination(icon=ft.Icons.TIMER_OUTLINED,      selected_icon=ft.Icons.TIMER,    label="Timer"),
        ]

    def _alumno_nav():
        return [
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT_OUTLINED,   selected_icon=ft.Icons.LIST_ALT, label="Rutinas"),
            ft.NavigationBarDestination(icon=ft.Icons.FITNESS_CENTER,       label="Entrenar"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY,              label="Historial"),
            ft.NavigationBarDestination(icon=ft.Icons.TIMER_OUTLINED,       selected_icon=ft.Icons.TIMER,   label="Timer"),
        ]

    def _profe_views():
        return [build_alumnos, build_timer]

    def _alumno_views():
        return [build_rutinas, build_entrenar, build_historial, build_timer]

    nav_bar = ft.NavigationBar(bgcolor=CARD, selected_index=0)

    def switch(idx):
        nav_bar.selected_index = idx
        views = _profe_views() if role[0] == "profe" else _alumno_views()
        content.content = views[idx](page)
        page.update()

    nav_bar.on_change = lambda e: switch(e.control.selected_index)

    def show_app():
        nav_bar.destinations = _profe_nav() if role[0] == "profe" else _alumno_nav()
        page.controls.clear()
        page.controls.append(
            ft.Column([content, nav_bar], expand=True, spacing=0)
        )
        switch(0)

    def on_login(session):
        role[0] = sb.role()
        show_app()

    def show_login():
        page.controls.clear()
        page.controls.append(build_login(page, on_login=on_login))
        page.update()

    session = sb.restore()
    if session:
        role[0] = sb.role()
        show_app()
    else:
        show_login()

ft.run(target=main)
