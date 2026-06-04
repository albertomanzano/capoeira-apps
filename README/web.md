# Web principal

Stack: SvelteKit 5 (Svelte 5 runes: `$state`, `$derived`, `$effect`) + [Supabase](supabase.md) + Netlify.

**URL producción**: https://capoeiracolectiva.netlify.app
**Dev local**: `cd web_colectivo && npm run dev` → localhost:5173
**Deploy**: `npm run build && npx netlify-cli deploy --prod --dir=build`

Sigue las [convenciones](convenciones.md) generales del proyecto.

## Rutas

```
/login  /registro  /reset-password
/rutinas  /rutinas/[id]
/entrenar  /historial  /timer
/alumnos  /alumnos/[id]
/descargas  /mi-perfil
```

**Navegación por rol**:
- Profe: Alumnos + Timer
- Alumno: Rutinas + Entrenar + Historial + Timer (+ ⚙ → /mi-perfil)

## Modelo de datos — rutinas

El campo `exercises` en Supabase almacena `Bloque[]`. Cada bloque agrupa ejercicios y puede lanzarse desde el timer de forma independiente.

```typescript
type Ex        = { name: string; duration_s: number }
type Bloque    = { name: string; exercises: Ex[] }
type BloqueLog = { name: string; exercises: Ex[]; marks: (number|null)[] }

// routines.exercises: Bloque[]
// training_logs.exercises: BloqueLog[]  (snapshot + marks por ejercicio)
```

Ver [supabase.md](supabase.md) para el schema completo. Migración: `web_colectivo/supabase_migration.sql`.

## Funcionalidades implementadas

- **Auth**: login, registro, reset-password, logout, cambio de contraseña
- **Rutinas**: crear/editar/borrar/copiar. Organizadas en bloques con ejercicios. Vista colapsable con resumen. Copiar bloque dentro del formulario. Botón ▶ por bloque que precarga el timer.
- **Entrenar**: seleccionar rutina → ejercicios agrupados por bloque → anotar marca numérica por ejercicio → guardar con fecha
- **Historial**: cards desplegables con bloques y marcas
- **Timer**: configurable (ejercicios, duración, pausas, rounds). Carga bloque desde rutina vía `localStorage`. Voz + beeps + colores por fase.
- **Alumnos**: el profe gestiona la lista (añadir/borrar)
- **Descargas**: página pública con APKs

## Estructura objetivo

```
/                    ← web pública (sin login): home, info, contacto
/members/            ← zona de miembros (login requerido)
    /rutinas         — gestión de rutinas
    /entrenar        — anotar entrenamiento
    /historial       — historial de entrenamientos
    /timer           — timer con voz
    /descargas       — descargar app de luthería
/alumnos             — solo profe (gestión de alumnos)
```

Actualmente las rutas de miembros están en la raíz (sin `/members/`). La web pública todavía no existe.

## Pendiente

- [ ] Construir web pública (home del Colectivo, info, contacto)
- [ ] Reorganizar rutas bajo `/members/`
- [ ] Ejecutar `supabase_migration.sql` en Supabase si no se ha hecho
- [ ] Dominio propio
- [ ] Migrar Netlify → Cloudflare Pages (Netlify sin créditos)
