import flet as ft
from datetime import date
from data import rutinas as rdb
from data import logs as ldb

GREEN  = "#4ade80"
CARD   = "#1a1a1a"
DIM    = "#555"
DIMMER = "#333"

def _fmt(s):
    if s < 60: return f"{s}s"
    m, r = divmod(s, 60)
    return f"{m}m{r}s" if r else f"{m}m"

def build_entrenar(page: ft.Page):
    state      = {"selected": None, "marks": [], "saved": False}
    main_col   = ft.Column([], spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def render():
        main_col.controls.clear()

        if state["saved"]:
            main_col.controls += [
                ft.Container(height=60),
                ft.Text("✓", size=48, color=GREEN, text_align=ft.TextAlign.CENTER),
                ft.Text("¡Guardado!", size=24, weight=ft.FontWeight.BOLD, color=GREEN, text_align=ft.TextAlign.CENTER),
                ft.Container(height=16),
                ft.ElevatedButton(
                    content=ft.Text("Otro entreno", color="#0f0f0f", weight=ft.FontWeight.BOLD),
                    bgcolor=GREEN, on_click=lambda e: reset(),
                ),
            ]
            page.update()
            return

        if state["selected"]:
            r = state["selected"]
            mark_fields = []

            def make_field(i):
                f = ft.TextField(
                    hint_text="—", keyboard_type=ft.KeyboardType.NUMBER,
                    width=90, text_size=18, text_align=ft.TextAlign.CENTER,
                    bgcolor="#111", border_color=DIMMER, focused_border_color=GREEN,
                    on_change=lambda e, idx=i: state["marks"].__setitem__(idx, float(e.control.value) if e.control.value else None),
                )
                mark_fields.append(f)
                return f

            ex_cards = [
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(ex["name"], size=15, weight=ft.FontWeight.W_600),
                            ft.Text(_fmt(ex["duration_s"]), size=12, color=DIM),
                        ], spacing=2, expand=True),
                        make_field(i),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=CARD, border_radius=10,
                    padding=ft.padding.symmetric(horizontal=16, vertical=14),
                )
                for i, ex in enumerate(r["exercises"])
            ]

            today = date.today().isoformat()
            date_field = ft.TextField(
                value=today, width=130, text_size=14,
                bgcolor="#111", border_color=DIMMER, focused_border_color=GREEN,
            )

            def save(e):
                ldb.save(
                    r["id"], r["name"], r["exercises"],
                    state["marks"], date_field.value or today,
                )
                state["saved"] = True
                render()

            main_col.controls += [
                ft.Row([
                    ft.TextButton(
                        f"← {r['name']}", on_click=lambda e: reset(),
                        style=ft.ButtonStyle(color="#888"),
                    ),
                    date_field,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                *ex_cards,
                ft.Container(height=8),
                ft.ElevatedButton(
                    content=ft.Text("Guardar entreno", color="#0f0f0f", weight=ft.FontWeight.BOLD),
                    bgcolor=GREEN, on_click=save, width=double_width(),
                ),
            ]
            page.update()
            return

        rutinas = rdb.get()
        main_col.controls.append(ft.Text("Entrenar", size=22, weight=ft.FontWeight.BOLD))
        if not rutinas:
            main_col.controls.append(
                ft.Text("Sin rutinas. Crea una primero.", color=DIM, text_align=ft.TextAlign.CENTER)
            )
        else:
            main_col.controls.append(ft.Text("ELIGE UNA RUTINA", size=11, color=DIM, weight=ft.FontWeight.W_600))
            for r in rutinas:
                main_col.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(r["name"], size=15, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{len(r['exercises'])} ejercicios", size=12, color=DIM),
                            ], spacing=2, expand=True),
                            ft.Text("›", size=22, color=DIMMER),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        bgcolor=CARD, border_radius=10,
                        padding=ft.padding.symmetric(horizontal=16, vertical=16),
                        on_click=lambda e, rr=r: pick(rr),
                        ink=True,
                    )
                )
        page.update()

    def double_width():
        return None

    def pick(r):
        state["selected"] = r
        state["marks"] = [None] * len(r["exercises"])
        state["saved"] = False
        render()

    def reset():
        state["selected"] = None
        state["marks"] = []
        state["saved"] = False
        render()

    render()
    return main_col
