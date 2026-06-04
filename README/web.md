# Web principal

Stack: SvelteKit 5 (Svelte 5 runes: `$state`, `$derived`, `$effect`) + [Supabase](supabase.md) + Cloudflare Pages.

**URL producción**: https://capoeira-colectiva.pages.dev
**Dev local**: `cd web_colectivo && npm run dev` → localhost:5173
**Deploy**: `cd web_colectivo && npm run build && wrangler pages deploy build --project-name=capoeira-colectiva --branch=main --commit-dirty=true`

Sigue las [convenciones](convenciones.md) generales del proyecto.

## Cloudflare Pages — notas de configuración

- `svelte.config.js`: `adapter-static` con `fallback: 'index.html'` (no `200.html` — Cloudflare no lo soporta como rewrite)
- `static/_redirects`: contiene `/* /index.html 200` para que SvelteKit maneje el routing client-side
- Supabase Auth: en el dashboard del proyecto → Authentication → URL Configuration, Site URL y Redirect URLs deben incluir `https://capoeira-colectiva.pages.dev/**`
- `login/+page.svelte`: el `redirectTo` del reset de contraseña apunta a `https://capoeira-colectiva.pages.dev/reset-password`

## Estructura de rutas

```
/                        ← web pública — pendiente de construir
/login  /registro  /reset-password

/members/                ← requiere login (auth guard en members/+layout.svelte)
    /rutinas             — gestión de rutinas; lanza el timer con ▶
    /historial           — historial agrupado por rutina
    /historial/nueva     — añadir entrada manual (sin pasar por el timer)
    /historial/[id]      — detalle de una sesión: marcas editables + borrar
    /timer               — timer con voz (solo accesible desde ▶ en rutinas)
    /descargas           — descargar app de luthería
    /mi-perfil           — nombre + cambiar contraseña + selector de voz + logout
```

**Navegación**: Rutinas / Historial (tabbar) + ⬇ Descargas + ⚙ Perfil (topbar). No hay distinción de rol en la UI.

**Flujo de entrenamiento**: Rutinas → ▶ lanza timer → reps se anotan durante el entreno → "Guardar entreno" al terminar → Historial.

## Modelo de datos — rutinas

```typescript
type Ex        = { name: string; duration_s: number }
type Bloque    = { name: string; exercises: Ex[] }
type BloqueLog = { name: string; exercises: Ex[]; marks: (number|null)[] }

// routines.exercises:      Bloque[]
// training_logs.exercises: BloqueLog[]
```

Ver [supabase.md](supabase.md) para el schema completo y políticas RLS.

## Convención: ejercicio "Descanso"

Un ejercicio llamado "Descanso" (insensible a mayúsculas) se trata como pausa explícita:

- **Rutinas**: no cuenta en el total de ejercicios ni aparece en los pills
- **Entrenar**: no se muestra (sin input de marca), no se guarda en el log
- **Historial**: no se muestra
- **Timer**: se trata como fase de tipo `pausa` (color teal, cuenta atrás), sin pausa automática antes

## Funcionalidades

- **Auth**: login, registro, reset-password, logout, cambio de contraseña
- **Rutinas**: crear/borrar/copiar (inmutables — no hay edición). Al crear, la fecha actual se añade automáticamente al nombre (`DD/MM/YYYY`). Bloques con ejercicios. Vista colapsable con resumen (bloques · ejercicios · duración total). Copiar bloque. Botón ▶ por bloque (lanza timer con ese bloque) y ▶ en la tarjeta (lanza timer con la rutina completa).
- **Timer**: lanzado siempre desde ▶ en Rutinas — sin acceso directo desde nav.
  - **Bloque**: usa los ejercicios del bloque; config disponible: pausa, bloques (repeticiones), descanso entre bloques.
  - **Rutina completa**: encadena todos los bloques en secuencia, se ejecuta una sola vez (ROUNDS=1). Config disponible: solo pausa. Barra de puntos por bloque.
  - Durante cada ejercicio aparece un input para anotar reps. Si existe una sesión anterior para esa rutina, muestra "Última vez: X" debajo del input (cargado de `training_logs` al inicio).
  - Al terminar: botón "Guardar entreno" → guarda en `training_logs`. Sin rutina cargada: pantalla "Ve a Rutinas".
  - Voz (Web Speech API) + beeps: ejercicios cada 5s; pausas cuenta atrás 10→4; beeps en 3, 2, 1. El selector de voz está en Perfil (mi-perfil), guardado en localStorage.
- **Historial**: agrupado por rutina. Cada grupo muestra nº de sesiones y fecha más reciente, ordenado por sesión más reciente arriba. Al desplegar un grupo aparecen las sesiones (fecha + resumen); al pulsar una sesión se navega a `/historial/[id]`. Botón "+ Añadir" para registrar una sesión manualmente sin pasar por el timer.
  - `/historial/[id]`: detalle con marcas editables (guardado onblur) y botón de borrar.
  - `/historial/nueva`: elegir rutina + fecha + rellenar marcas → guarda en `training_logs`.
- **Descargas**: APK de luthería (requiere login)
- **Perfil** (`mi-perfil`): nombre, cambiar contraseña, selector de voz preferida, logout.

## Compatibilidad datos antiguos

Rutinas creadas antes de junio 2026 usaban `Ex[]` plano. `normalize()` en `rutinas/+page.svelte` las convierte a `Bloque[]` al cargar. Ver [supabase.md](supabase.md) para el SQL de limpieza.

## Pendiente

- [ ] Construir web pública (home del Colectivo, info, contacto)
- [ ] Dominio propio
- [x] Migrar Netlify → Cloudflare Pages ✓ (2026-06-04)
