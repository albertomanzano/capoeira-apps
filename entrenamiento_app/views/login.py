import flet as ft
from data import supabase as sb

GREEN  = "#4ade80"
BG     = "#0f0f0f"
CARD   = "#1a1a1a"

def build_login(page: ft.Page, on_login):
    email_field = ft.TextField(
        label="Email", keyboard_type=ft.KeyboardType.EMAIL,
        bgcolor=CARD, border_color="#333", focused_border_color=GREEN,
        text_size=16,
    )
    pass_field = ft.TextField(
        label="Contraseña", password=True, can_reveal_password=True,
        bgcolor=CARD, border_color="#333", focused_border_color=GREEN,
        text_size=16,
    )
    error_text = ft.Text("", color="#ef4444", size=13)
    btn = ft.ElevatedButton(
        content=ft.Text("Entrar", size=16, weight=ft.FontWeight.BOLD, color="#0f0f0f"),
        bgcolor=GREEN, width=320, height=52,
    )

    def do_login(e):
        error_text.value = ""
        btn.disabled = True
        page.update()
        try:
            session = sb.login(email_field.value.strip(), pass_field.value)
            on_login(session)
        except Exception as ex:
            error_text.value = "Email o contraseña incorrectos"
            btn.disabled = False
            page.update()

    btn.on_click = do_login
    pass_field.on_submit = do_login

    return ft.Container(
        content=ft.Column([
            ft.Container(height=60),
            ft.Text("Capoeira", size=32, weight=ft.FontWeight.BOLD, color=GREEN),
            ft.Text("Entrenamiento", size=16, color="#555"),
            ft.Container(height=40),
            email_field,
            pass_field,
            error_text,
            ft.Container(height=8),
            btn,
        ], spacing=14, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        padding=32,
        bgcolor=BG,
    )
