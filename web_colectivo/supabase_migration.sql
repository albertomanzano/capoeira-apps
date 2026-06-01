-- Tabla de rutinas
CREATE TABLE IF NOT EXISTS routines (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  name       text NOT NULL,
  exercises  jsonb NOT NULL DEFAULT '[]',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE routines ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_all" ON routines
  FOR ALL TO authenticated
  USING  (user_id = auth.uid() OR is_profe())
  WITH CHECK (user_id = auth.uid());

-- Tabla de registros de entrenamiento
CREATE TABLE IF NOT EXISTS training_logs (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  routine_id   uuid REFERENCES routines(id) ON DELETE SET NULL,
  routine_name text NOT NULL,
  exercises    jsonb NOT NULL DEFAULT '[]',
  marks        jsonb NOT NULL DEFAULT '[]',
  date         date NOT NULL DEFAULT CURRENT_DATE,
  created_at   timestamptz DEFAULT now()
);

ALTER TABLE training_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_all" ON training_logs
  FOR ALL TO authenticated
  USING  (user_id = auth.uid() OR is_profe())
  WITH CHECK (user_id = auth.uid());
