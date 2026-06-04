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

El campo `exercises` en Supabase almacena `Bloque[]`. Cada bloque agrupa ejercicios y se puede lanzar de forma independiente desde el timer.

```typescript
type Ex        = { name: string; duration_s: number }
type Bloque    = { name: string; exercises: Ex[] }
type BloqueLog = { name: string; exercises: Ex[]; marks: (number|null)[] }

// routines.exercises:     Bloque[]
// training_logs.exercises: BloqueLog[]  (snapshot + marks por ejercicio)
```

Ver [supabase.md](supabase.md) para el schema completo y políticas RLS.

## Funcionalidades implementadas

- **Auth**: login, registro, reset-password, logout, cambio de contraseña
- **Rutinas**: crear/editar/borrar/copiar. Organizadas en bloques. Vista colapsable. Copiar bloque. Botón ▶ por bloque que precarga el timer vía `localStorage`.
- **Entrenar**: seleccionar rutina → ejercicios por bloque → anotar marca numérica → guardar con fecha
- **Historial**: cards desplegables con bloques y marcas
- **Timer**: configurable (ejercicios, duración, pausas, rounds). Carga bloque desde rutina. Voz (Web Speech API) + beeps + colores por fase.
- **Alumnos**: el profe gestiona la lista (añadir/borrar)
- **Descargas**: APK de luthería (requiere login)

## Pendiente

- [ ] Construir web pública (home del Colectivo, info, contacto)
- [ ] Dominio propio
- [ ] Migrar Netlify → Cloudflare Pages (Netlify sin créditos)
