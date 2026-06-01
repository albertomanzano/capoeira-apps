-- ═══════════════════════════════════════════════
-- Migración v3 — pegar en Supabase SQL Editor
-- ═══════════════════════════════════════════════

-- 1. Tabla de categorías
create table categories (
  id   uuid primary key default gen_random_uuid(),
  name text not null unique
);
alter table categories enable row level security;
create policy "Profes gestionan categorías" on categories
  for all using (exists (select 1 from profiles where id = auth.uid() and role = 'profe'));
create policy "Alumnos ven categorías" on categories
  for select using (auth.uid() is not null);

-- 2. Insertar las categorías que ya existían
insert into categories (name) values ('Habilidad'), ('Movilidad'), ('Fuerza');

-- 3. Añadir category_id a exercises y migrar los datos existentes
alter table exercises add column category_id uuid references categories on delete set null;

update exercises e
set category_id = c.id
from categories c
where lower(c.name) = e.category;

-- 4. Eliminar la columna de texto antigua
alter table exercises drop column category;
