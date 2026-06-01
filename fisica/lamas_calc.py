#!/usr/bin/env python3
"""
Calculadora de lamas para atabaque de capoeira.

Uso interactivo:
    python lamas_calc.py

Uso por argumentos (plancha opcional, default 50×200):
    python lamas_calc.py d_boca d_barriga d_pie altura grosor_mm n_lamas [ancho largo]
    python lamas_calc.py 26 26 13 70 18 19
    python lamas_calc.py 26 26 13 70 18 19 25 200
"""
import math
import sys


def lamas_por_plancha(w_max, w_min, L_blank, plancha_w, plancha_l, k, hay_barriga):
    if not hay_barriga:
        w_franja = w_max + w_min + k
        pitch    = w_franja + k
        n_pares  = int(plancha_w / pitch)
        por_secc = n_pares * 2
    else:
        pitch    = w_max + k
        por_secc = int(plancha_w / pitch)
    n_secciones = int(plancha_l / L_blank)
    return por_secc * n_secciones


def calcular(d_boca, d_barriga, d_pie, h_total, grosor_mm, n_lamas,
             plancha_w=50.0, plancha_l=200.0, kerf_mm=3.0):

    t = grosor_mm / 10
    k = kerf_mm / 10

    r_boca    = d_boca    / 2
    r_barriga = d_barriga / 2
    r_pie     = d_pie     / 2

    h_barriga   = h_total * 0.65
    hay_barriga = d_barriga > max(d_boca, d_pie)

    # ── Ángulos ───────────────────────────────────────────────────────────
    bisel = 180.0 / n_lamas
    tan_b = math.tan(math.radians(bisel))

    def w_ext(r):
        return 2.0 * (r + t) * tan_b

    w_boca    = w_ext(r_boca)
    w_barriga = w_ext(r_barriga)
    w_pie     = w_ext(r_pie)

    # ── Longitud de la lama ───────────────────────────────────────────────
    if hay_barriga:
        L_lama   = (math.hypot(h_barriga,           r_barriga - r_pie) +
                    math.hypot(h_total - h_barriga, r_barriga - r_boca))
        ang_pie  = math.degrees(math.atan2(r_barriga - r_pie,  h_barriga))
        ang_boca = math.degrees(math.atan2(r_barriga - r_boca, h_total - h_barriga))
    else:
        L_lama   = math.hypot(h_total, abs(r_boca - r_pie))
        ang_cono = math.degrees(math.atan2(abs(r_boca - r_pie), h_total))
        ang_pie  = ang_cono
        ang_boca = ang_cono

    L_blank = math.ceil(L_lama) + 5

    # ── Cálculo con las planchas dadas ────────────────────────────────────
    w_max = max(w_boca, w_barriga)
    w_min = w_pie

    if not hay_barriga:
        w_franja   = w_max + w_min + k
        pitch      = w_franja + k
        n_franjas  = int(plancha_w / pitch)
        lamas_secc = n_franjas * 2
        metodo = f"par anidado ({w_franja:.1f} cm/franja → 2 lamas)"
    else:
        pitch      = w_max + k
        n_franjas  = int(plancha_w / pitch)
        lamas_secc = n_franjas
        metodo = f"blank rectangular {w_max:.1f} cm (barriga impide anidar)"

    n_secciones       = int(plancha_l / L_blank)
    total_por_plancha = lamas_secc * n_secciones
    n_planchas        = math.ceil(n_lamas / total_por_plancha) if total_por_plancha else 0
    sobrantes         = total_por_plancha * n_planchas - n_lamas

    # ── Tabla de anchos estándar (largo fijo = plancha_l) ─────────────────
    anchos_std = [15, 20, 25, 30, 40, 50]
    filas_tabla = []
    for a in anchos_std:
        lpp = lamas_por_plancha(w_max, w_min, L_blank, a, plancha_l, k, hay_barriga)
        np  = math.ceil(n_lamas / lpp) if lpp else 99
        ok  = "✓" if np <= 2 else "✗"
        filas_tabla.append((a, lpp, np, ok))

    # ── Salida ────────────────────────────────────────────────────────────
    S = "─" * 50

    print(f"\n{'═'*52}")
    print(f"  CALCULADORA DE LAMAS — ATABAQUE DE CAPOEIRA")
    print(f"{'═'*52}")

    print(f"\n  INSTRUMENTO")
    print(f"  {S}")
    print(f"  Boca    (arriba)   Ø interior  {d_boca:6.1f} cm")
    print(f"  Barriga (máximo)   Ø interior  {d_barriga:6.1f} cm" +
          ("  ← bulge" if hay_barriga else ""))
    print(f"  Pie     (abajo)    Ø interior  {d_pie:6.1f} cm")
    print(f"  Altura total                   {h_total:6.1f} cm")
    print(f"  Número de lamas                {n_lamas:6d}")
    print(f"  Grosor de la madera            {grosor_mm:6.0f} mm")

    # desplazamiento de la raya interior para el bisel lateral
    offset_bisel_mm = grosor_mm * tan_b   # = t × tan(α)

    # anchuras cara interior (= cara exterior − 2 × offset)
    wi_boca    = w_boca    - 2 * offset_bisel_mm / 10
    wi_barriga = w_barriga - 2 * offset_bisel_mm / 10
    wi_pie     = w_pie     - 2 * offset_bisel_mm / 10

    print(f"\n  ÁNGULOS DE CORTE")
    print(f"  {S}")
    print(f"  Bisel lateral — AMBOS cantos   {bisel:6.2f}°")
    print(f"    → Inclinar la sierra {bisel:.1f}° y pasar cada canto largo")
    print(f"    → dos pasadas por lama (un canto, luego el otro)")
    print(f"  Corte extremo PIE  (abajo)     {ang_pie:6.1f}°  respecto a la perpendicular")
    print(f"  Corte extremo BOCA (arriba)    {ang_boca:6.1f}°  respecto a la perpendicular")
    if not hay_barriga and abs(ang_pie - ang_boca) < 0.1:
        print(f"    → Mismo ángulo en ambos extremos (frustum simple)")

    print(f"\n  MARCADO DEL BISEL  (offset = grosor × tan(bisel))")
    print(f"  {S}")
    print(f"  offset = {grosor_mm:.0f} mm × tan({bisel:.2f}°) = {offset_bisel_mm:.1f} mm por canto")
    print(f"")
    print(f"  Cara exterior  →  cara interior  (diferencia = 2 × {offset_bisel_mm:.1f} mm)")
    print(f"  {'─'*44}")
    print(f"  Boca:    {w_boca:.2f} cm  →  {wi_boca:.2f} cm")
    if hay_barriga:
        print(f"  Barriga: {w_barriga:.2f} cm  →  {wi_barriga:.2f} cm")
    print(f"  Pie:     {w_pie:.2f} cm  →  {wi_pie:.2f} cm")
    print(f"")
    print(f"  Cómo usar: marca el ancho exterior en la cara de fuera,")
    print(f"  luego desplaza {offset_bisel_mm:.1f} mm hacia dentro en cada canto")
    print(f"  para marcar la cara interior. Corta uniendo ambas rayas.")

    print(f"\n  DIMENSIONES DE CADA LAMA  (cara exterior)")
    print(f"  {S}")
    print(f"  Largo del blank         {L_blank:5.0f} cm   (lama real ≈ {L_lama:.1f} cm)")
    print(f"  Ancho en la boca        {w_boca:5.2f} cm")
    print(f"  Ancho en la barriga     {w_barriga:5.2f} cm" +
          ("  ← máximo" if hay_barriga else ""))
    print(f"  Ancho en el pie         {w_pie:5.2f} cm")

    SCALE = 6
    def bar(w):
        return "█" * max(1, round(w * SCALE))

    print(f"\n  Perfil (proporcional, cara exterior):")
    print(f"  boca     {w_boca:.1f} cm  {bar(w_boca)}")
    if hay_barriga:
        print(f"  barriga  {w_barriga:.1f} cm  {bar(w_barriga)}")
    print(f"  pie      {w_pie:.1f} cm  {bar(w_pie)}")

    print(f"\n  PLANCHAS ELEGIDAS  {plancha_w:.0f}×{plancha_l:.0f} cm, {grosor_mm:.0f} mm")
    print(f"  {S}")
    print(f"  Método de corte: {metodo}")
    print(f"  Secciones de {L_blank:.0f} cm por plancha    {n_secciones}")
    print(f"  Lamas por sección                  {lamas_secc}")
    print(f"  Lamas por plancha                  {total_por_plancha}")
    print(f"  Lamas necesarias                   {n_lamas}")
    print()
    print(f"  ┌{'─'*36}┐")
    print(f"  │  Planchas a comprar:   {n_planchas:>3}           │")
    print(f"  │  Lamas sobrantes:      {sobrantes:>3}           │")
    print(f"  └{'─'*36}┘")

    print(f"\n  COMPARATIVA DE ANCHOS  (largo fijo {plancha_l:.0f} cm, grosor {grosor_mm:.0f} mm)")
    print(f"  {S}")
    print(f"  {'ancho':>6}  {'lamas/plancha':>14}  {'planchas':>9}  {'≤2?':>4}")
    print(f"  {'─'*6}  {'─'*14}  {'─'*9}  {'─'*4}")
    for a, lpp, np, ok in filas_tabla:
        marca = " ← recomendado" if (np <= 2 and a == min(x[0] for x in filas_tabla if x[2] <= 2)) else ""
        print(f"  {a:>5} cm  {lpp:>14}  {np:>9}  {ok:>4}{marca}")
    print()


def main():
    if len(sys.argv) in (7, 9):
        pw = float(sys.argv[7]) if len(sys.argv) == 9 else 50.0
        pl = float(sys.argv[8]) if len(sys.argv) == 9 else 200.0
        calcular(
            float(sys.argv[1]),
            float(sys.argv[2]),
            float(sys.argv[3]),
            float(sys.argv[4]),
            float(sys.argv[5]),
            int(sys.argv[6]),
            plancha_w=pw, plancha_l=pl,
        )
        return

    def ask(msg, default=None):
        suffix = f" [{default}]" if default is not None else ""
        val = input(f"  {msg}{suffix}: ").strip()
        return val if val else str(default)

    print("\n  Calculadora de lamas de atabaque de capoeira")
    print("  " + "─" * 44)
    d_boca    = float(ask("Ø interior boca    (arriba)  [cm]"))
    d_barriga = float(ask("Ø interior barriga (máximo)  [cm]"))
    d_pie     = float(ask("Ø interior pie     (abajo)   [cm]"))
    h_total   = float(ask("Altura total                 [cm]"))
    grosor_mm = float(ask("Grosor de la madera          [mm]"))
    n_lamas   = int(  ask("Número de lamas                  "))
    plancha_w = float(ask("Ancho de plancha             [cm]", default=50))
    plancha_l = float(ask("Largo de plancha             [cm]", default=200))
    calcular(d_boca, d_barriga, d_pie, h_total, grosor_mm, n_lamas,
             plancha_w=plancha_w, plancha_l=plancha_l)


if __name__ == "__main__":
    main()
