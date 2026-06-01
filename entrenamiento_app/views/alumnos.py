import flet as ft
from data import supabase as sb

GREEN  = "#4ade80"
CARD   = "#1a1a1a"
DIM    = "#555"
DIMMER = "#333"

def build_alumnos(page: ft.Page):
    students   = [None]
    new_field  = ft.TextField(
        label="Nombre del alumno", bgcolor=CARD,
        border_color=DIMMER, focused_border_color=GREEN,
    )
    list_col   = ft.Column([], spacing=8)
    error_text = ft.Text("", color="#ef4444", size=12)

    def load():
        r = sb.db().from_("students").select("id,name").order("name").execute()
        students[0] = r.data or []
        list_col.controls.clear()
        for s in students[0]:
            sid, sname = s["id"], s["name"]
            list_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(sname, size=16, weight=ft.FontWeight.W_600, expand=True),
                        ft.IconButton(
                            ft.Icons.CLOSE, icon_color=DIMMER, icon_size=18,
                            on_click=lambda e, i=sid, n=sname: confirm_delete(i, n),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=CARD, border_radius=10, padding=ft.padding.symmetric(horizontal=16, vertical=12),
                )
            )
        if not students[0]:
            list_col.controls.append(ft.Text("Sin alumnos todavía.", color=DIM, text_align=ft.TextAlign.CENTER))
        page.update()

    def confirm_delete(id, name):
        def do_delete(e):
            dlg.open = False
            sb.db().from_("students").delete().eq("id", id).execute()
            load()
            page.update()
        def cancel(e):
            dlg.open = False
            page.update()
        dlg = ft.AlertDialog(
            title=ft.Text(f"¿Borrar a {name}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel),
                ft.TextButton("Borrar", on_click=do_delete, style=ft.ButtonStyle(color="#ef4444")),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def add(e):
        name = new_field.value.strip()
        if not name:
            return
        sb.db().from_("students").insert({"name": name}).execute()
        new_field.value = ""
        load()

    new_field.on_submit = add
    load()

    return ft.Column([
        ft.Text("Alumnos", size=22, weight=ft.FontWeight.BOLD),
        ft.Container(height=4),
        list_col,
        ft.Divider(color=DIMMER, height=32),
        ft.Text("AÑADIR ALUMNO", size=11, color=DIM, weight=ft.FontWeight.W_600),
        new_field,
        error_text,
        ft.ElevatedButton(
            content=ft.Text("Añadir", color="#0f0f0f", weight=ft.FontWeight.BOLD),
            bgcolor=GREEN, on_click=add,
        ),
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
