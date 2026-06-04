# Supabase

Proyecto: `biihtcuzcpyfagccrmij`. Compartido entre la [web](web.md) y la [app de luthería](lutheria.md).
Migración a ejecutar en SQL Editor: `web_colectivo/supabase_migration.sql`.

## Tablas activas

**profiles** — rol de cada usuario (`profe` | `alumno`)
**students** — alumnos gestionados por el profe
**routines** — rutinas de entrenamiento
**training_logs** — historial de entrenamientos

## Schema rutinas y logs

```sql
routines (
  id uuid PK, user_id uuid→auth.users,
  name text,
  exercises jsonb,   -- Bloque[] (ver más abajo)
  created_at timestamptz
)

training_logs (
  id uuid PK, user_id uuid→auth.users,
  routine_id uuid→routines, routine_name text,
  exercises jsonb,   -- BloqueLog[] (ver más abajo)
  marks jsonb,       -- [] vacío (marcas embebidas en exercises)
  date date, created_at timestamptz
)
```

## Modelo de datos (junio 2026)

```typescript
type Ex        = { name: string; duration_s: number }
type Bloque    = { name: string; exercises: Ex[] }
type BloqueLog = { name: string; exercises: Ex[]; marks: (number|null)[] }
```

Antes de junio 2026 `exercises` almacenaba `Ex[]` plano. Ya no hay registros con el formato antiguo.

## Políticas RLS

Todas las tablas tienen RLS habilitado. Política en `routines` y `training_logs`:

```sql
USING  (user_id = auth.uid() OR is_profe())
WITH CHECK (user_id = auth.uid())
```

## Política RLS

Simplificada a `user_id = auth.uid()` en ambas tablas. La `supabase_migration.sql` incluye el `DROP POLICY IF EXISTS` + `CREATE POLICY` correcto. Si las tablas ya existen y la política es la antigua (con `is_profe()`), hay que volver a ejecutar la migración.
