-- ═══════════════════════════════════════════════
-- Capoeira app — esquema Supabase
-- Pegar en: Supabase Dashboard → SQL Editor → Run
-- ═══════════════════════════════════════════════

-- Perfil de usuario (profe o alumno)
create table profiles (
  id    uuid references auth.users on delete cascade primary key,
  name  text not null,
  role  text not null check (role in ('profe', 'alumno'))
);
alter table profiles enable row level security;
create policy "Perfil propio" on profiles
  for all using (auth.uid() = id);
create policy "Profes ven todos los perfiles" on profiles
  for select using (
    exists (select 1 from profiles where id = auth.uid() and role = 'profe')
  );

-- Biblioteca de ejercicios (compartida entre todos los profes)
create table exercises (
  id    uuid primary key default gen_random_uuid(),
  name  text not null,
  unit  text not null check (unit in ('segundos', 'reps', 'ninguna'))
);
alter table exercises enable row level security;
create policy "Profes gestionan ejercicios" on exercises
  for all using (
    exists (select 1 from profiles where id = auth.uid() and role = 'profe')
  );
create policy "Alumnos ven ejercicios" on exercises
  for select using (auth.uid() is not null);

-- Alumnos (pueden tener cuenta de usuario o no)
create table students (
  id      uuid primary key default gen_random_uuid(),
  name    text not null,
  user_id uuid references auth.users  -- null hasta que el alumno tenga cuenta
);
alter table students enable row level security;
create policy "Profes gestionan alumnos" on students
  for all using (
    exists (select 1 from profiles where id = auth.uid() and role = 'profe')
  );
create policy "Alumno ve su propio perfil" on students
  for select using (user_id = auth.uid());

-- Asignación de ejercicios a alumnos (7 slots)
create table student_slots (
  student_id  uuid references students on delete cascade,
  slot_index  integer check (slot_index between 0 and 6),
  exercise_id uuid references exercises on delete set null,
  target      numeric,  -- objetivo (segundos o reps)
  primary key (student_id, slot_index)
);
alter table student_slots enable row level security;
create policy "Profes gestionan slots" on student_slots
  for all using (
    exists (select 1 from profiles where id = auth.uid() and role = 'profe')
  );
create policy "Alumno ve sus slots" on student_slots
  for select using (
    exists (select 1 from students where id = student_id and user_id = auth.uid())
  );

-- Sesiones de entrenamiento
create table sessions (
  id         uuid primary key default gen_random_uuid(),
  date       date not null,
  created_by uuid references auth.users
);
alter table sessions enable row level security;
create policy "Profes gestionan sesiones" on sessions
  for all using (
    exists (select 1 from profiles where id = auth.uid() and role = 'profe')
  );

-- Alumnos en cada sesión
create table session_students (
  session_id uuid references sessions on delete cascade,
  student_id uuid references students on delete cascade,
  primary key (session_id, student_id)
);
alter table session_students enable row level security;
create policy "Profes gestionan asistencia" on session_students
  for all using (
    exists (select 1 from profiles where id = auth.uid() and role = 'profe')
  );

-- Marcas por sesión, alumno y slot
create table marks (
  session_id    uuid references sessions on delete cascade,
  student_id    uuid references students on delete cascade,
  slot_index    integer check (slot_index between 0 and 6),
  value         numeric,   -- para segundos/reps
  done          boolean,   -- para elasticidades (sin métrica)
  primary key (session_id, student_id, slot_index)
);
alter table marks enable row level security;
create policy "Profes gestionan marcas" on marks
  for all using (
    exists (select 1 from profiles where id = auth.uid() and role = 'profe')
  );
create policy "Alumno ve sus marcas" on marks
  for select using (
    exists (select 1 from students where id = student_id and user_id = auth.uid())
  );
