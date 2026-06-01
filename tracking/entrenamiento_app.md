# Tracking: App de entrenamiento (Flet/Android)

## Decisión
Sustituye la web SvelteKit para uso móvil. La web del Colectivo queda en standby para un futuro.
App separada de la luthería. Ambas se descargarán desde la web del Colectivo cuando esté lista.

## Estado general
Pendiente de iniciar. Stack: Python + Flet 0.84.0 + Supabase (mismo proyecto que la web).

## Stack
- Python + Flet 0.84.0
- Virtualenv: `atabaque_venv/` (compartido con luthería)
- Backend: Supabase (`biihtcuzcpyfagccrmij`) — mismas tablas que la web
- Audio: nativo Android → timer funciona en background y con pantalla apagada

## Estructura prevista
```
entrenamiento_app/
├── data/
│   ├── supabase.py   — cliente Supabase (auth + queries)
│   ├── alumnos.py    — gestión de alumnos
│   ├── rutinas.py    — CRUD rutinas + ejercicios
│   └── logs.py       — training_logs
├── views/
│   ├── login.py      — auth email/password
│   ├── alumnos.py    — lista alumnos (profe)
│   ├── rutinas.py    — CRUD rutinas
│   ├── entrenar.py   — seleccionar rutina + anotar marks
│   ├── historial.py  — historial de entrenamientos
│   └── timer.py      — timer con voz + audio background
└── app.py            — navegación + auth guard
```

## Roles
- **Profe**: Alumnos + Timer
- **Alumno**: Rutinas + Entrenar + Historial + Timer

## Base de datos Supabase (ya existente)
Tablas: `profiles`, `students`, `routines`, `training_logs`
Migración: `web_colectivo/supabase_migration.sql`

## Completado
(nada aún)

## Pendiente
- [ ] Scaffold inicial: `app.py` + navegación + auth guard
- [ ] `models/supabase.py`: cliente + login/logout/session
- [ ] `views/login.py`
- [ ] `views/alumnos.py` (profe)
- [ ] `views/rutinas.py`
- [ ] `views/entrenar.py`
- [ ] `views/historial.py`
- [ ] `views/timer.py` con audio en background
- [ ] Build APK y prueba en dispositivo
