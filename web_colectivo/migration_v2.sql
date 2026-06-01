-- ═══════════════════════════════════════════════
-- Migración v2 — pegar en Supabase SQL Editor
-- ═══════════════════════════════════════════════

-- 1. Categoría en ejercicios
alter table exercises
  add column if not exists category text not null default 'habilidad'
  check (category in ('habilidad', 'movilidad', 'fuerza'));

-- 2. Snapshot del ejercicio en cada marca
--    Permite ver el nombre correcto en sesiones históricas
--    aunque el alumno cambie de ejercicio después
alter table marks
  add column if not exists exercise_id uuid references exercises on delete set null;
