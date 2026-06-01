# Tracking: Web del Colectivo / App de entrenamiento SvelteKit

## Estado general
En producción. Desplegado en Netlify.

## URLs
- **Producción**: https://capoeiracolectiva.netlify.app
- **Dev local**: http://localhost:5173 (en `web_colectivo/`, `npm run dev`)

## Stack
- SvelteKit 5 (Svelte 5 runes: `$state`, `$derived`, `$effect`)
- Supabase (PostgreSQL + Auth) — proyecto `biihtcuzcpyfagccrmij`
- Netlify (adapter-static + `_redirects` para SPA routing)

## Deploy
Build: `npm run build` → `netlify deploy --dir build --prod`

## Estructura de rutas
```
/                        — redirect (profe→/alumnos, alumno→/rutinas)
/login                   — login email/password
/registro                — registro de nuevos usuarios
/reset-password          — reset de contraseña
/mi-perfil               — nombre + cambiar contraseña (alumno)
/alumnos                 — lista de alumnos, añadir/borrar (profe)
/alumnos/[id]            — nombre del alumno (stub)
/rutinas                 — CRUD de rutinas por alumno
/rutinas/[id]            — editar rutina existente
/entrenar                — seleccionar rutina + anotar marks
/historial               — historial de entrenamientos
/timer                   — timer con voz, beeps y descanso entre rounds
```

## Navegación por rol
- **Profe**: Alumnos + Timer
- **Alumno**: Rutinas + Entrenar + Historial + Timer (+ icono ⚙ → /mi-perfil)

## Base de datos (Supabase)
Tablas activas: `profiles`, `students`, `routines`, `training_logs`

### routines
```
id uuid PK, user_id uuid→auth.users, name text,
exercises jsonb  -- [{name, duration_s}, ...]
created_at timestamptz
```

### training_logs
```
id uuid PK, user_id uuid→auth.users, routine_id uuid→routines,
routine_name text, exercises jsonb (snapshot),
marks jsonb  -- [number|null, ...]  uno por ejercicio en orden
date date, created_at timestamptz
```

RLS en ambas: `user_id = auth.uid() OR is_profe()`

**Migración**: `web_colectivo/supabase_migration.sql` — ejecutar en Supabase SQL Editor.

## Funcionalidades completadas
- **Auth**: login, registro, reset, logout, cambio de contraseña
- **Rutinas**: crear (nombre + lista ejercicios con nombre y duración en segundos), editar, borrar
- **Entrenar**: seleccionar rutina → anotar número por ejercicio → guardar con fecha
- **Historial**: lista de entrenamientos con ejercicios y marks
- **Timer**: ejercicios × minutos + pausa entre ejercicios + rounds + **descanso entre rounds** (color naranja, voz)
- **Alumnos**: el profe gestiona la lista de alumnos (add/remove)

## Pendiente
- [ ] Ejecutar `supabase_migration.sql` en Supabase (tablas routines + training_logs)
- [ ] Árbol de habilidades
- [ ] Página pública del Colectivo (info, contacto)
- [ ] Link de descarga APK luthería
- [ ] Dominio propio
