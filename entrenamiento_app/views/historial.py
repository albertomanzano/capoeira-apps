import flet as ft
from data import logs as ldb

GREEN  = "#4ade80"
CARD   = "#1a1a1a"
DIM    = "#555"
DIMMER = "#333"
MUTED  = "#aaa"

def _fmt(s):
    if s < 60: return f"{s}s"
    m, r = divmod(s, 60)
    return f"{m}m{r}s" if r else f"{m}m"

def _fmt_date(d):
    y, m, day = d.split("-")
    return f"{day}/{m}/{y[2:]}"

def build_historial(page: ft.Page):
    list_col = ft.Column([], spacing=10)

    def confirm_delete(id):
        def do(e):
            dlg.open = False; ldb.delete(id); load(); page.update()
        def cancel(e):
            dlg.open = False; page.update()
        dlg = ft.AlertDialog(
            title=ft.Text("¿Borrar esta entrada?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel),
                ft.TextButton("Borrar", on_click=do, style=ft.ButtonStyle(color="#ef4444")),
            ],
        )
        page.dialog = dlg; dlg.open = True; page.update()

    def load():
        logs = ldb.get()
        list_col.controls.clear()
        for log in logs:
            ex_rows = [
                ft.Row([
                    ft.Text(ex["name"], size=13, color=MUTED, expand=True),
                    ft.Text(_fmt(ex["duration_s"]), size=12, color=DIMMER, width=40, text_align=ft.TextAlign.RIGHT),
                    ft.Text(
                        str(log["marks"][i]) if log["marks"][i] is not None else "—",
                        size=13, color=GREEN, weight=ft.FontWeight.BOLD,
                        width=40, text_align=ft.TextAlign.RIGHT,
                    ),
                ])
                for i, ex in enumerate(log["exercises"])
            ]
            list_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(_fmt_date(log["date"]), size=11, color=DIM, weight=ft.FontWeight.W_700),
                                ft.Text(log["routine_name"], size=15, weight=ft.FontWeight.BOLD),
                            ], spacing=2, expand=True),
                            ft.IconButton(
                                ft.Icons.CLOSE, icon_color=DIMMER, icon_size=16,
                                on_click=lambda e, i=log["id"]: confirm_delete(i),
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        *ex_rows,
                    ], spacing=6),
                    bgcolor=CARD, border_radius=10,
                    padding=ft.padding.symmetric(horizontal=16, vertical=14),
                )
            )
        if not logs:
            list_col.controls.append(
                ft.Text("Sin entrenamientos todavía.", color=DIM, text_align=ft.TextAlign.CENTER)
            )
        page.update()

    load()

    return ft.Column([
        ft.Text("Historial", size=22, weight=ft.FontWeight.BOLD),
        list_col,
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10)
