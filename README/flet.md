# Flet 0.84.0 — quirks de la API

Referencia rápida para evitar errores silenciosos en la [app de luthería](lutheria.md). Para el build Android ver [android.md](android.md).

## API

- `Tab` usa `label=` no `text=`
- `ft.Icons.X` mayúsculas (no `ft.icons.X`)
- `ft.alignment.Alignment(0,0)` — no `ft.alignment.center`
- `ElevatedButton(content=ft.Text(...))` — no `text=`
- `scroll=` en `ft.Column`, no en `ft.Container`
- `ft.Image` requiere `src` obligatorio — no instanciar sin él

## Threading y rendering

- `async def main` + `page.run_task()` + `run_in_executor` — `threading.Thread` no hace flush
- Errores en handlers: fallan silenciosamente — añadir try/except siempre

## Colores

- Hex 6 dígitos siempre (`"#ffffff"`) — los de 3 hacen el texto invisible en Android
- Misma regla en [convenciones.md](convenciones.md) para CSS web
