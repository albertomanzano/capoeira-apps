# Web principal

Stack: SvelteKit 5 (Svelte 5 runes: `$state`, `$derived`, `$effect`) + [Supabase](supabase.md) + Netlify.

**URL producción**: https://capoeiracolectiva.netlify.app
**Dev local**: `cd web_colectivo && npm run dev` → localhost:5173
**Deploy**: `npm run build && npx netlify-cli deploy --prod --dir=build`

Sigue las [convenciones](convenciones.md) generales del proyecto.

## Estructura de rutas

```
/                        ← web pública — pendiente de construir
/login  /registro  /reset-password

/members/                ← requiere login (auth guard en members/+layout.svelte)
    /rutinas             — gestión de rutinas
    /rutinas/[id]        — editar rutina
    /entrenar            — anotar entrenamiento
    /historial           — historial de entrenamientos
    /timer               — timer con voz
    /descargas           — descargar app de luthería
    /alumnos             — solo profe (gestión de alumnos)
    /alumnos/[id]
    /mi-perfil           — nombre + cambiar contraseña
```

**Navegación por rol**:
- Profe: Alumnos (topbar) + Rutinas / Entrenar / Historial / Timer (tabbar) + ⬇ Descargas + ⚙ Perfil
- Alumno: Rutinas / Entrenar / Historial / Timer (tabbar) + ⬇ Descargas + ⚙ Perfil

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
- **Rutinas**: crear/editar/borrar/copiar. Bloques con ejercicios. Vista colapsable con resumen (bloques · ejercicios · duración total). Copiar bloque. Botón ▶ por bloque (lanza timer con ese bloque) y ▶ en la tarjeta (lanza timer con la rutina completa).
- **Entrenar**: seleccionar rutina → ejercicios por bloque → anotar marca → guardar con fecha. No muestra "Descanso".
- **Historial**: cards desplegables con bloques, marcas y duración total. No muestra "Descanso".
- **Timer**: dos modos:
  - **Manual**: configura número de ejercicios, duración, pausa, rondas y descanso entre rondas
  - **Bloque**: lanzado desde ▶ de un bloque — usa los ejercicios del bloque, ignora config de ejercicios/duración
  - **Rutina completa**: lanzado desde ▶ de la tarjeta de rutina — encadena todos los bloques. La barra de puntos muestra una fila por bloque con el nombre a la izquierda. El header muestra el nombre del bloque activo.
  - Voz (Web Speech API) + beeps:
    - **Ejercicios**: voz cada 5s de tiempo transcurrido; beeps en 3, 2, 1
    - **Pausas**: voz cuenta atrás 10→4; beeps en 3, 2, 1
- **Alumnos**: el profe gestiona la lista (añadir/borrar)
- **Descargas**: APK de luthería (requiere login)

## Compatibilidad datos antiguos

Rutinas creadas antes de junio 2026 usaban `Ex[]` plano. `normalize()` en `rutinas/+page.svelte` las convierte a `Bloque[]` al cargar. Ver [supabase.md](supabase.md) para el SQL de limpieza.

## Pendiente

- [ ] Construir web pública (home del Colectivo, info, contacto)
- [ ] Dominio propio
- [ ] Migrar Netlify → Cloudflare Pages (Netlify sin créditos)
