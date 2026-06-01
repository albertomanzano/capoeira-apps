from data import supabase as sb

def get():
    r = sb.db().from_("routines").select("id,name,exercises,created_at").order("created_at", desc=True).execute()
    return r.data or []

def create(name, exercises):
    u = sb.user()
    sb.db().from_("routines").insert({"user_id": u.id, "name": name, "exercises": exercises}).execute()

def update(id, name, exercises):
    sb.db().from_("routines").update({"name": name, "exercises": exercises}).eq("id", id).execute()

def delete(id):
    sb.db().from_("routines").delete().eq("id", id).execute()
