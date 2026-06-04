# Supabase

Proyecto: `biihtcuzcpyfagccrmij`. Compartido entre la [web](web.md) y la [app de luthería](lutheria.md).
Migración: `web_colectivo/supabase_migration.sql` — ejecutar en SQL Editor si las tablas no existen.

## Tablas activas

**profiles** — rol de cada usuario (`profe` | `alumno`)
**students** — alumnos gestionados por el profe
**routines** — rutinas de entrenamiento
**training_logs** — historial de entrenamientos

## Schema

```sql
routines (
  id uuid PK, user_id uuid→auth.users,
  name text,
  exercises jsonb,   -- Bloque[]
  created_at timestamptz
)

training_logs (
  id uuid PK, user_id uuid→auth.users,
  routine_id uuid→routines, routine_name text,
  exercises jsonb,   -- BloqueLog[] (snapshot con marks embebidas)
  marks jsonb,       -- [] (legacy, no se usa)
  date date, created_at timestamptz
)
```

## Modelo de datos

```typescript
type Ex        = { name: string; duration_s: number }
type Bloque    = { name: string; exercises: Ex[] }
type BloqueLog = { name: string; exercises: Ex[]; marks: (number|null)[] }
```

## Políticas RLS

`user_id = auth.uid()` en todas las tablas — cada usuario solo ve sus propios datos.

```sql
-- aplicado en supabase_migration.sql
DROP POLICY IF EXISTS "own_all" ON routines;
CREATE POLICY "own_all" ON routines
  FOR ALL TO authenticated
  USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());
```

La versión antigua usaba `OR is_profe()` en la cláusula USING, función que nunca se definió. La migración incluye el DROP para reemplazarla correctamente.

## Compatibilidad formato antiguo

Antes de junio 2026 `exercises` almacenaba `Ex[]` plano (sin bloques). El frontend normaliza automáticamente al cargar (`normalize()` en rutinas/+page.svelte), pero los datos viejos en Supabase se pueden borrar con:

```sql
DELETE FROM routines
WHERE exercises != '[]'::jsonb
  AND (exercises->0->>'duration_s') IS NOT NULL
  AND (exercises->0->'exercises') IS NULL;
```
