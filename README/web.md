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
    /rutinas/[id]        — editar rutina
    /historial           — historial de entrenamientos
    /timer               — timer con voz (solo accesible desde ▶ en rutinas)
    /descargas           — descargar app de luthería
    /alumnos             — solo profe (gestión de alumnos)
    /alumnos/[id]
    /mi-perfil           — nombre + cambiar contraseña
```

**Navegación por rol**:
- Profe: Alumnos (topbar) + Rutinas / Historial (tabbar) + ⬇ Descargas + ⚙ Perfil
- Alumno: Rutinas / Historial (tabbar) + ⬇ Descargas + ⚙ Perfil

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
- **Rutinas**: crear/editar/borrar/copiar. Al guardar (nueva o editada), la fecha actual se añade automáticamente al nombre (`DD/MM/YYYY`). Editar = borrar fila antigua + insertar nueva (inmutable). El formulario de edición muestra el nombre sin la fecha. Bloques con ejercicios. Vista colapsable con resumen (bloques · ejercicios · duración total). Copiar bloque. Botón ▶ por bloque (lanza timer con ese bloque) y ▶ en la tarjeta (lanza timer con la rutina completa).
- **Timer**: lanzado siempre desde ▶ en Rutinas — sin acceso directo desde nav.
  - **Bloque**: usa los ejercicios del bloque; config disponible: pausa, bloques (repeticiones), descanso entre bloques.
  - **Rutina completa**: encadena todos los bloques en secuencia, se ejecuta una sola vez (ROUNDS=1). Config disponible: solo pausa. Barra de puntos por bloque.
  - Durante cada ejercicio (y la pausa siguiente) aparece un input para anotar reps.
  - Al terminar: botón "Guardar entreno" → guarda en `training_logs`. Sin rutina cargada: pantalla "Ve a Rutinas".
  - Voz (Web Speech API) + beeps: ejercicios cada 5s; pausas cuenta atrás 10→4; beeps en 3, 2, 1.
- **Historial**: cards desplegables con bloques, marcas y duración total. No muestra "Descanso".
- **Alumnos**: el profe gestiona la lista (añadir/borrar)
- **Descargas**: APK de luthería (requiere login)

## Compatibilidad datos antiguos

Rutinas creadas antes de junio 2026 usaban `Ex[]` plano. `normalize()` en `rutinas/+page.svelte` las convierte a `Bloque[]` al cargar. Ver [supabase.md](supabase.md) para el SQL de limpieza.

## Pendiente

- [ ] Construir web pública (home del Colectivo, info, contacto)
- [ ] Dominio propio
- [x] Migrar Netlify → Cloudflare Pages ✓ (2026-06-04)
