import json
from pathlib import Path
from supabase import create_client

_URL  = "https://biihtcuzcpyfagccrmij.supabase.co"
_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpaWh0Y3V6Y3B5ZmFnY2NybWlqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg1ODMyNTgsImV4cCI6MjA5NDE1OTI1OH0.ItT8EDO80jAYg9nPgE7on7_0KW7vgt82-trEgGGehwY"
_SESSION_FILE = Path.home() / ".cap_entreno.json"

_client = None

def _c():
    global _client
    if _client is None:
        _client = create_client(_URL, _KEY)
    return _client

def db():
    return _c()

def login(email, password):
    res = _c().auth.sign_in_with_password({"email": email, "password": password})
    _persist(res.session)
    return res.session

def logout():
    try:
        _c().auth.sign_out()
    except Exception:
        pass
    _SESSION_FILE.unlink(missing_ok=True)

def restore():
    if not _SESSION_FILE.exists():
        return None
    try:
        d = json.loads(_SESSION_FILE.read_text())
        res = _c().auth.set_session(d["access_token"], d["refresh_token"])
        _persist(res.session)
        return res.session
    except Exception:
        _SESSION_FILE.unlink(missing_ok=True)
        return None

def _persist(session):
    if session:
        _SESSION_FILE.write_text(json.dumps({
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }))

def user():
    s = _c().auth.get_session()
    return s.user if s else None

def role():
    u = user()
    if not u:
        return None
    r = _c().from_("profiles").select("role").eq("id", u.id).single().execute()
    return (r.data or {}).get("role")
