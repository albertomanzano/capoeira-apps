import flet as ft
from data import rutinas as db

GREEN  = "#4ade80"
CARD   = "#1a1a1a"
CARD2  = "#141414"
DIM    = "#555"
DIMMER = "#333"
MUTED  = "#aaa"

def _fmt(s):
    if s < 60: return f"{s}s"
    m, r = divmod(s, 60)
    return f"{m}m{r}s" if r else f"{m}m"

def build_rutinas(page: ft.Page):
    list_col   = ft.Column([], spacing=8)
    form_area  = ft.Column([], visible=False, spacing=10)
    error_text = ft.Text("", color="#ef4444", size=12)

    name_field = ft.TextField(
        label="Nombre de la rutina", bgcolor=CARD2,
        border_color=DIMMER, focused_border_color=GREEN,
    )

    ex_col     = ft.Column([], spacing=8)
    _edit_id   = [None]
    _exercises  = [None]

    def _ex_row(idx):
        name_f = ft.TextField(
            hint_text="Nombre", bgcolor=CARD2, border_color=DIMMER,
            focused_border_color=GREEN, expand=True, text_size=14,
            value=_exercises[0][idx]["name"],
            on_change=lambda e, i=idx: _exercises[0].__setitem__(i, {**_exercises[0][i], "name": e.control.value}),
        )
        dur_f = ft.TextField(
            hint_text="seg", bgcolor=CARD2, border_color=DIMMER,
            focused_border_color=GREEN, width=72, text_size=14,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(_exercises[0][idx]["duration_s"]),
            on_change=lambda e, i=idx: _exercises[0].__setitem__(
                i, {**_exercises[0][i], "duration_s": int(e.control.value or 60)}
            ),
        )
        rm_btn = ft.IconButton(
            ft.Icons.CLOSE, icon_color=DIM, icon_size=18,
            on_click=lambda e, i=idx: remove_ex(i),
        )
        return ft.Row([name_f, dur_f, ft.Text("s", color=DIM, size=13), rm_btn])

    def rebuild_ex_col():
        ex_col.controls.clear()
        for i in range(len(_exercises[0])):
            ex_col.controls.append(_ex_row(i))

    def add_ex(e):
        _exercises[0].append({"name": "", "duration_s": 60})
        rebuild_ex_col()
        page.update()

    def remove_ex(idx):
        _exercises[0].pop(idx)
        rebuild_ex_col()
        page.update()

    def open_form(rutina=None):
        _edit_id[0] = rutina["id"] if rutina else None
        name_field.value = rutina["name"] if rutina else ""
        _exercises[0] = list(rutina["exercises"]) if rutina else [{"name": "", "duration_s": 60}]
        rebuild_ex_col()
        error_text.value = ""
        form_area.visible = True
        page.update()

    def close_form(e=None):
        form_area.visible = False
        error_text.value = ""
        page.update()

    def save(e):
        exs = [x for x in _exercises[0] if x["name"].strip()]
        if not name_field.value.strip():
            error_text.value = "Ponle nombre a la rutina"
            page.update(); return
        if not exs:
            error_text.value = "Añade al menos un ejercicio"
            page.update(); return
        if _edit_id[0]:
            db.update(_edit_id[0], name_field.value.strip(), exs)
        else:
            db.create(name_field.value.strip(), exs)
        close_form()
        load()

    form_area.controls = [
        ft.Text("", ref=ft.Ref()),  # spacer
        name_field,
        ft.Text("EJERCICIOS", size=11, color=DIM, weight=ft.FontWeight.W_600),
        ex_col,
        ft.TextButton("+ Ejercicio", on_click=add_ex, style=ft.ButtonStyle(color=GREEN)),
        error_text,
        ft.Row([
            ft.ElevatedButton(
                content=ft.Text("Guardar", color="#0f0f0f", weight=ft.FontWeight.BOLD),
                bgcolor=GREEN, on_click=save, expand=True,
            ),
            ft.OutlinedButton("Cancelar", on_click=close_form, expand=True),
        ], spacing=10),
    ]

    def confirm_delete(id, name):
        def do(e):
            dlg.open = False; db.delete(id); load(); page.update()
        def cancel(e):
            dlg.open = False; page.update()
        dlg = ft.AlertDialog(
            title=ft.Text(f'¿Borrar "{name}"?'),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel),
                ft.TextButton("Borrar", on_click=do, style=ft.ButtonStyle(color="#ef4444")),
            ],
        )
        page.dialog = dlg; dlg.open = True; page.update()

    def load():
        rutinas = db.get()
        list_col.controls.clear()
        for r in rutinas:
            pills = [
                ft.Container(
                    content=ft.Text(f"{x['name']} {_fmt(x['duration_s'])}", size=12, color=MUTED),
                    bgcolor=CARD2, border_radius=6, padding=ft.padding.symmetric(horizontal=8, vertical=3),
                )
                for x in r["exercises"]
            ]
            list_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(r["name"], size=15, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{len(r['exercises'])} ejercicios", size=11, color=DIM),
                            ft.Row(pills, wrap=True, spacing=6, run_spacing=4),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.IconButton(ft.Icons.EDIT, icon_color=DIM, icon_size=18,
                                          on_click=lambda e, rr=r: open_form(rr)),
                            ft.IconButton(ft.Icons.CLOSE, icon_color=DIMMER, icon_size=18,
                                          on_click=lambda e, i=r["id"], n=r["name"]: confirm_delete(i, n)),
                        ], spacing=0),
                    ]),
                    bgcolor=CARD, border_radius=10,
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                )
            )
        if not rutinas:
            list_col.controls.append(
                ft.Text("Sin rutinas. Crea la primera.", color=DIM, text_align=ft.TextAlign.CENTER)
            )
        page.update()

    load()

    return ft.Column([
        ft.Row([
            ft.Text("Rutinas", size=22, weight=ft.FontWeight.BOLD, expand=True),
            ft.ElevatedButton(
                content=ft.Text("+ Nueva", color="#0f0f0f", weight=ft.FontWeight.BOLD, size=13),
                bgcolor=GREEN, on_click=lambda e: open_form(),
                height=36,
            ),
        ]),
        form_area,
        list_col,
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
