from datetime import date
from data import supabase as sb

def get(limit=60):
    r = sb.db().from_("training_logs").select("id,date,routine_name,exercises,marks").order("date", desc=True).limit(limit).execute()
    return r.data or []

def save(routine_id, routine_name, exercises, marks, fecha=None):
    u = sb.user()
    sb.db().from_("training_logs").insert({
        "user_id":      u.id,
        "routine_id":   routine_id,
        "routine_name": routine_name,
        "exercises":    exercises,
        "marks":        marks,
        "date":         fecha or date.today().isoformat(),
    }).execute()

def delete(id):
    sb.db().from_("training_logs").delete().eq("id", id).execute()
