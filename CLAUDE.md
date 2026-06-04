# Capoeira Colectiva

Dos productos: una [web](README/web.md) (SvelteKit + Supabase) y una [app de luthería](README/lutheria.md) descargable (Python + Flet).

## Al iniciar cada conversación

Leer siempre la skill de gestión de conocimiento: `/home/alberto/.claude/skills/knowledge-management/`

## Responsabilidades de Claude

- **Conocimiento**: actualizar CLAUDE.md y README/ durante la sesión, sin esperar al final
- **Git**: commit y push tras cada sesión — Alberto no gestiona git directamente
- **Deploy web**: `npm run build && npx netlify-cli deploy --prod --dir=build` desde `web_colectivo/`
- **Supabase**: documentar cambios de schema en [supabase.md](README/supabase.md) y recordar a Alberto ejecutar las migraciones

## El proyecto

```
capoeira_apps/
├── web_colectivo/    → web principal (SvelteKit) — ver README/web.md
├── luteria_app/      → app luthería (Python/Flet) — ver README/lutheria.md
├── fisica/           → modelos físicos — ver README/fisica.md
└── README/           → base de conocimiento del proyecto
```

## Navegar el conocimiento

| Estás trabajando en... | Lee primero |
|---|---|
| Web, SvelteKit, rutas, deploy | [web.md](README/web.md) |
| Supabase, schema, RLS, bug de guardado | [supabase.md](README/supabase.md) |
| App luthería, vistas, modelos | [lutheria.md](README/lutheria.md) |
| Física del berimbau o atabaque | [fisica.md](README/fisica.md) |
| Build APK, Android | [android.md](README/android.md) |
| Flet API quirks, threading, colores | [flet.md](README/flet.md) |
| Convenciones, virtualenv, git | [convenciones.md](README/convenciones.md) |
