import flet as ft
import threading
import time
import numpy as np

try:
    import sounddevice as sd
    _AUDIO = True
except Exception:
    _AUDIO = False

SR = 44100
GREEN  = "#4ade80"
TEAL   = "#4ecdc4"
AMBER  = "#f59e0b"
ORANGE = "#ff6b35"
CARD   = "#1a1a1a"
DIM    = "#555"
DIMMER = "#333"

# ── Audio ────────────────────────────────────────────────────────────────────

def _play(notes):
    if not _AUDIO:
        return
    total = int(SR * (max(d + dur for _, dur, _, d in notes) + 0.1))
    buf = np.zeros(total, dtype=np.float32)
    for freq, dur, vol, delay in notes:
        start = int(SR * delay)
        t = np.linspace(0, dur, int(SR * dur))
        wave = np.sin(2 * np.pi * freq * t) * vol
        end = min(start + len(wave), total)
        buf[start:end] += wave[:end - start]
    np.clip(buf, -1, 1, out=buf)
    sd.play(buf, SR)

def beep_warning():
    threading.Thread(target=_play, args=[[(660, 0.08, 0.25, 0)]], daemon=True).start()

def beep_transition():
    threading.Thread(target=_play, args=[[(880,.08,.4,0),(880,.08,.4,.15),(880,.08,.4,.30),(1320,.35,.5,.50)]], daemon=True).start()

def beep_end_round():
    threading.Thread(target=_play, args=[[(880,.12,.5,0),(880,.12,.5,.18),(1320,.35,.6,.36),(1320,.45,.6,.90)]], daemon=True).start()

# ── Timer state (module-level → persiste entre cambios de vista) ─────────────

_cfg = {"exercises": 7, "exercise_min": 1, "pause_sec": 30, "rounds": 2, "round_break_sec": 60}
_CFG_LIMITS = {
    "exercises":      (1, 12, 1),
    "exercise_min":   (1, 10, 1),
    "pause_sec":      (10, 120, 5),
    "rounds":         (1, 5, 1),
    "round_break_sec":(0, 300, 30),
}

_state = {
    "running": False, "started": False, "finished": False,
    "in_break": False, "round": 0, "phase": 0, "time_left": 0,
    "phases": [],
}
_thread      = [None]
_running_ref = [False]
_page_ref    = [None]
_rebuild_ref = [None]

def _build_phases():
    dur = _cfg["exercise_min"] * 60
    phases = []
    for i in range(_cfg["exercises"]):
        phases.append({"name": f"Ejercicio {i+1}", "type": "ejercicio", "duration": dur})
        if i < _cfg["exercises"] - 1:
            phases.append({"name": "Pausa", "type": "pausa", "duration": _cfg["pause_sec"]})
    return phases

def _reset_state():
    _state.update({"running": False, "started": False, "finished": False,
                   "in_break": False, "round": 0, "phase": 0,
                   "phases": _build_phases()})
    _state["time_left"] = _state["phases"][0]["duration"]

def _advance():
    s = _state
    s["phase"] += 1
    if s["phase"] >= len(s["phases"]):
        s["phase"] = 0
        if s["round"] + 1 >= _cfg["rounds"]:
            _running_ref[0] = False
            s["running"] = False
            s["finished"] = True
            beep_end_round()
            return
        if _cfg["round_break_sec"] > 0:
            s["in_break"] = True
            s["time_left"] = _cfg["round_break_sec"]
            beep_end_round()
            return
        s["round"] += 1
    beep_transition()
    s["time_left"] = s["phases"][s["phase"]]["duration"] if not s["in_break"] else _cfg["round_break_sec"]

def _timer_loop():
    while _running_ref[0]:
        time.sleep(1)
        if not _running_ref[0]:
            break
        s = _state
        s["time_left"] -= 1
        tl = s["time_left"]

        if tl in (3, 2, 1):
            beep_warning()

        if s["in_break"]:
            if tl <= 0:
                s["in_break"] = False
                s["round"] += 1
                s["phase"] = 0
                beep_transition()
                s["time_left"] = s["phases"][0]["duration"]
        else:
            elapsed = s["phases"][s["phase"]]["duration"] - tl
            if elapsed > 0 and elapsed % 5 == 0 and tl > 3:
                pass  # TODO: voz
            if tl <= 0:
                _advance()

        if _rebuild_ref[0] and _page_ref[0]:
            _rebuild_ref[0]()
            _page_ref[0].update()

# ── View ─────────────────────────────────────────────────────────────────────

def build_timer(page: ft.Page):
    _page_ref[0] = page

    if not _state["phases"]:
        _reset_state()

    # display refs
    round_text  = ft.Text("", size=14, color=DIM)
    phase_label = ft.Text("", size=12, weight=ft.FontWeight.W_700, color="#888")
    phase_name  = ft.Text("", size=22, weight=ft.FontWeight.BOLD)
    timer_text  = ft.Text("", size=80, weight=ft.FontWeight.W_800,
                          font_family="monospace")
    progress    = ft.ProgressBar(value=0, width=320, height=5, color=GREEN, bgcolor=DIMMER)
    next_text   = ft.Text("", size=14, color=DIM)
    start_btn   = ft.ElevatedButton(height=56, width=160)
    reset_btn   = ft.ElevatedButton(
        content=ft.Text("Reset", size=16, color="#aaa"),
        bgcolor=CARD, height=56, width=100,
        on_click=lambda e: do_reset(),
    )

    cfg_labels = {
        "exercises":       "Ejercicios",
        "exercise_min":    "Min / ejercicio",
        "pause_sec":       "Pausa (s)",
        "rounds":          "Rondas",
        "round_break_sec": "Descanso rondas (s)",
    }

    def _stepper(key):
        val_text = ft.Text(str(_cfg[key]), size=14, color="#ccc", width=40, text_align=ft.TextAlign.CENTER)
        mn, mx, step = _CFG_LIMITS[key]
        def dec(e):
            _cfg[key] = max(mn, _cfg[key] - step)
            val_text.value = str(_cfg[key])
            if not _state["started"]:
                _reset_state()
            update_display()
            page.update()
        def inc(e):
            _cfg[key] = min(mx, _cfg[key] + step)
            val_text.value = str(_cfg[key])
            if not _state["started"]:
                _reset_state()
            update_display()
            page.update()
        return ft.Row([
            ft.IconButton(ft.Icons.REMOVE, icon_size=18, icon_color="#aaa", on_click=dec,
                          disabled=_state["running"]),
            val_text,
            ft.IconButton(ft.Icons.ADD, icon_size=18, icon_color="#aaa", on_click=inc,
                          disabled=_state["running"]),
        ], spacing=0)

    cfg_rows = ft.Column([
        ft.Row([
            ft.Text(cfg_labels[k], size=13, color="#777", expand=True),
            _stepper(k),
        ])
        for k in cfg_labels
    ], spacing=4)

    cfg_panel = ft.Container(
        content=cfg_rows,
        bgcolor=CARD, border_radius=10,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        visible=True,
    )

    def update_display():
        s = _state
        phases = s["phases"]
        if not phases:
            return

        if s["finished"]:
            round_text.value  = ""
            phase_label.value = ""
            phase_name.value  = ""
            timer_text.value  = "¡Fin!"
            timer_text.color  = GREEN
            progress.value    = 1.0
            progress.color    = GREEN
            next_text.value   = ""
            start_btn.content = ft.Text("Empezar", size=16, weight=ft.FontWeight.BOLD, color="#0f0f0f")
            start_btn.bgcolor = GREEN
            cfg_panel.visible = False
            page.update()
            return

        cur_phase = phases[s["phase"]]
        in_break  = s["in_break"]
        dur       = _cfg["round_break_sec"] if in_break else cur_phase["duration"]
        elapsed   = dur - s["time_left"]
        pct       = max(0, min(1, elapsed / dur)) if dur > 0 else 0
        is_pausa  = not in_break and cur_phase["type"] == "pausa"
        is_warn   = s["time_left"] <= 5 and not is_pausa and not in_break

        round_text.value  = f"Ronda {s['round']+1} de {_cfg['rounds']}"
        timer_text.value  = f"{elapsed//60}:{elapsed%60:02d}"

        if in_break:
            phase_label.value = "DESCANSO"
            phase_label.color = AMBER
            phase_name.value  = f"Ronda {s['round']+1} → {s['round']+2}"
            timer_text.color  = AMBER
            progress.color    = AMBER
        elif is_pausa:
            phase_label.value = "PAUSA"
            phase_label.color = TEAL
            phase_name.value  = ""
            timer_text.color  = TEAL
            progress.color    = TEAL
        elif is_warn:
            phase_label.value = "EJERCICIO"
            phase_label.color = ORANGE
            phase_name.value  = cur_phase["name"]
            timer_text.color  = ORANGE
            progress.color    = ORANGE
        else:
            phase_label.value = "EJERCICIO"
            phase_label.color = "#888"
            phase_name.value  = cur_phase["name"]
            timer_text.color  = "#ffffff"
            progress.color    = GREEN

        progress.value = pct

        # next info
        next_ph = phases[s["phase"] + 1] if s["phase"] + 1 < len(phases) else None
        is_last_round = s["round"] >= _cfg["rounds"] - 1
        if in_break:
            next_text.value = f"A continuación: Ronda {s['round']+2}"
        elif next_ph is None and is_last_round:
            next_text.value = "Último ejercicio"
        elif next_ph is None:
            next_text.value = "A continuación: Descanso" if _cfg["round_break_sec"] > 0 else f"Ronda {s['round']+2}"
        elif next_ph["type"] == "pausa":
            next_text.value = "A continuación: Pausa"
        else:
            next_text.value = f"A continuación: {next_ph['name']}"

        if s["running"]:
            start_btn.content = ft.Text("Pausar", size=16, weight=ft.FontWeight.BOLD, color="#0f0f0f")
            start_btn.bgcolor = "#facc15"
            cfg_panel.visible = False
        elif s["started"]:
            start_btn.content = ft.Text("Continuar", size=16, weight=ft.FontWeight.BOLD, color="#0f0f0f")
            start_btn.bgcolor = GREEN
            cfg_panel.visible = False
        else:
            start_btn.content = ft.Text("Empezar", size=16, weight=ft.FontWeight.BOLD, color="#0f0f0f")
            start_btn.bgcolor = GREEN
            cfg_panel.visible = True

    _rebuild_ref[0] = update_display

    def toggle_start(e):
        s = _state
        if s["finished"]:
            do_reset(); return
        if s["running"]:
            _running_ref[0] = False
            s["running"] = False
        else:
            if not s["started"]:
                s["started"] = True
                beep_transition()
            _running_ref[0] = True
            s["running"] = True
            t = threading.Thread(target=_timer_loop, daemon=True)
            _thread[0] = t
            t.start()
        update_display()
        page.update()

    def do_reset():
        _running_ref[0] = False
        _reset_state()
        update_display()
        page.update()

    start_btn.on_click = toggle_start
    update_display()

    return ft.Column([
        ft.Column([
            round_text,
            phase_label,
            phase_name,
            timer_text,
            progress,
            ft.Container(height=4),
            next_text,
            ft.Container(height=16),
            ft.Row([start_btn, reset_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        ft.Container(height=24),
        cfg_panel,
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=0)
