#!/usr/bin/env python3
"""
Modelo acústico del atabaque / congas
======================================
Calcula y visualiza:
  - Modos de vibración del parche (membrana circular, funciones de Bessel)
  - Modos de resonancia de la caja cónica (ecuación de Webster)
  - Acoplamiento entre ambos

Geometría basada en medidas reales de atabaques brasileños.
"""

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider, RadioButtons
from matplotlib.lines import Line2D
from scipy.special import jn, jn_zeros


# ─── Presets por instrumento ─────────────────────────────────────────────────
#
# Medidas de referencia:
#   Rum    h~90cm, Ø cabeza ~28cm, Ø base ~18cm  (ángulo cono ~3.2°)
#   Rumpi  h~70cm, Ø cabeza ~24cm, Ø base ~15cm  (ángulo cono ~3.3°)
#   Lê     h~55cm, Ø cabeza ~20cm, Ø base ~12cm  (ángulo cono ~3.5°)
#
# Parámetros del parche: cuero de cabra típico.
# Tensión inicial elegida para dar fundamental ~130-160 Hz en cada tamaño.

PRESETS = {
    'Rum': {
        'a':     0.140,   # radio parche [m]
        'T':     1000.0,  # tensión [N/m]
        'rho':   0.400,   # densidad superficial [kg/m²]
        'L':     0.900,   # altura caja [m]
        'r_top': 0.140,   # radio superior (= radio parche) [m]
        'r_bot': 0.090,   # radio inferior, abierto [m]
    },
    'Rumpi': {
        'a':     0.120,
        'T':     1200.0,
        'rho':   0.380,
        'L':     0.700,
        'r_top': 0.120,
        'r_bot': 0.075,
    },
    'Lê': {
        'a':     0.100,
        'T':     1500.0,
        'rho':   0.360,
        'L':     0.550,
        'r_top': 0.100,
        'r_bot': 0.060,
    },
}

C_AIR  = 343.0   # velocidad del sonido en aire [m/s]
MAX_M  = 3       # máx. diámetros nodales a calcular
MAX_N  = 3       # máx. círculos nodales a calcular
N_SHELL = 10     # primeros N modos de la caja


# ─── Cálculo de modos ────────────────────────────────────────────────────────

def membrane_modes(a, T, rho):
    """Frecuencias propias de membrana circular tensa (condición borde fijo)."""
    c_m = np.sqrt(T / rho)
    modes = []
    for m in range(MAX_M + 1):
        zeros = jn_zeros(m, MAX_N)
        for n_idx, z in enumerate(zeros):
            f = z * c_m / (2.0 * np.pi * a)
            modes.append(dict(m=m, n=n_idx + 1, z=z, f=f,
                               label=f'({m},{n_idx+1})'))
    return sorted(modes, key=lambda x: x['f'])


def shell_modes(L, r_bot):
    """
    Frecuencias de resonancia de caja cónica (aprox. abierto-abierto).
    Incluye corrección de extremo en la abertura inferior.
    """
    delta = 0.6 * r_bot     # corrección de extremo de Rayleigh
    L_eff = L + delta
    return [dict(n=n, f=n * C_AIR / (2.0 * L_eff)) for n in range(1, N_SHELL + 1)]


# ─── Dibujo del patrón nodal de un modo del parche ───────────────────────────

def draw_mode_shape(ax, m, n):
    r     = np.linspace(0, 1, 250)
    theta = np.linspace(0, 2 * np.pi, 250)
    R, TH = np.meshgrid(r, theta)
    z_mn  = jn_zeros(m, n)[-1]
    Z     = jn(m, z_mn * R) * np.cos(m * TH)
    X, Y  = R * np.cos(TH), R * np.sin(TH)
    ax.contourf(X, Y, Z, levels=30, cmap='RdBu_r')
    ax.contour(X, Y, Z, levels=[0], colors='k', linewidths=1.2)
    ax.set_aspect('equal')
    ax.axis('off')


# ─── Dibujo del perfil de la caja ────────────────────────────────────────────

def draw_shell_profile(ax, L, r_top, r_bot):
    ax.clear()
    y = np.array([0, L])
    r = np.array([r_bot, r_top])
    ax.fill_betweenx(y,  r, -r, alpha=0.25, color='saddlebrown')
    ax.plot( r, y, color='saddlebrown', lw=2)
    ax.plot(-r, y, color='saddlebrown', lw=2)
    ax.axhline(L, color='gray', lw=1.5, ls='--', label='parche')
    ax.axhline(0, color='steelblue', lw=1.0, ls=':',  label='abertura')
    ax.set_xlim(-r_top * 2, r_top * 2)
    ax.set_ylim(-0.05, L * 1.15)
    ax.set_xlabel('radio [m]', fontsize=8)
    ax.set_ylabel('altura [m]', fontsize=8)
    angle_deg = np.degrees(np.arctan((r_top - r_bot) / L))
    ax.set_title(f'Perfil caja\nα = {angle_deg:.1f}°', fontsize=9)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=7)


# ─── Dibujo del espectro y patrones nodales ──────────────────────────────────

COLORS_M = plt.cm.tab10(np.linspace(0, 0.6, MAX_M + 1))


def redraw(fig, axes, p):
    ax_spec, ax_shell, ax_modes = axes

    mems   = membrane_modes(p['a'], p['T'], p['rho'])
    shells = shell_modes(p['L'], p['r_bot'])
    f_fund = mems[0]['f']

    # ── Espectro ─────────────────────────────────────────────────────────────
    ax_spec.clear()

    for mode in mems:
        col = COLORS_M[mode['m']]
        ax_spec.axvline(mode['f'], color=col, alpha=0.8, lw=1.5)
        ax_spec.text(mode['f'], 1.08, mode['label'],
                     rotation=90, fontsize=7, ha='center', va='bottom', color=col)

    for s in shells:
        ax_spec.axvline(s['f'], color='gray', alpha=0.45, lw=1.2, ls='--')
        ax_spec.text(s['f'], 0.52, f"n={s['n']}",
                     rotation=90, fontsize=6.5, ha='center', va='bottom', color='gray')

    # Marcar coincidencias (acoplamiento)
    tol = 0.06   # tolerancia relativa
    for mode in mems:
        for s in shells:
            if abs(mode['f'] - s['f']) / mode['f'] < tol:
                ax_spec.axvspan(mode['f'] - 3, mode['f'] + 3,
                                color='gold', alpha=0.35, zorder=0)

    ax_spec.set_xlim(0, min(mems[-1]['f'] * 1.15, 3500))
    ax_spec.set_ylim(0, 1.55)
    ax_spec.set_xlabel('Frecuencia [Hz]', fontsize=9)
    ax_spec.set_yticks([])
    ax_spec.set_title(
        f'Espectro de modos   |   fundamental parche: {f_fund:.0f} Hz   |   '
        f'1er modo caja: {shells[0]["f"]:.0f} Hz',
        fontsize=9
    )

    legend_handles = (
        [Line2D([0], [0], color=COLORS_M[m], lw=1.5) for m in range(MAX_M + 1)] +
        [Line2D([0], [0], color='gray',  lw=1.2, ls='--'),
         Line2D([0], [0], color='gold',  lw=6,   alpha=0.5)]
    )
    legend_labels = (
        [f'parche m={m}' for m in range(MAX_M + 1)] +
        ['caja armónico n', 'acoplamiento']
    )
    ax_spec.legend(legend_handles, legend_labels,
                   fontsize=7, loc='upper right', ncol=2)

    # ── Perfil caja ──────────────────────────────────────────────────────────
    draw_shell_profile(ax_shell, p['L'], p['r_top'], p['r_bot'])

    # ── Patrones nodales (primeros 5 modos del parche) ───────────────────────
    first5 = mems[:5]
    for k, (ax_m, mode) in enumerate(zip(ax_modes, first5)):
        ax_m.clear()
        draw_mode_shape(ax_m, mode['m'], mode['n'])
        col = COLORS_M[mode['m']]
        ax_m.set_title(f"{mode['label']}\n{mode['f']:.0f} Hz",
                       fontsize=8, color=col)

    fig.canvas.draw_idle()


# ─── Layout principal ─────────────────────────────────────────────────────────

def build_ui(preset_name='Rum'):
    p = dict(PRESETS[preset_name])

    fig = plt.figure(figsize=(15, 9))
    fig.patch.set_facecolor('#f8f8f8')
    fig.suptitle('Modelo acústico — Atabaque', fontsize=14, fontweight='bold', y=0.97)

    gs = gridspec.GridSpec(
        3, 6,
        figure=fig,
        left=0.06, right=0.97,
        top=0.91, bottom=0.22,
        hspace=0.55, wspace=0.45
    )

    ax_spec  = fig.add_subplot(gs[0:2, 1:])
    ax_shell = fig.add_subplot(gs[0:2, 0])
    ax_modes = [fig.add_subplot(gs[2, k]) for k in range(5)]
    # el 6º hueco lo usamos para info textual
    ax_info = fig.add_subplot(gs[2, 5])
    ax_info.axis('off')

    axes = (ax_spec, ax_shell, ax_modes)

    # ── Sliders ───────────────────────────────────────────────────────────────
    slider_defs = [
        # (etiqueta, clave, min, max)
        ('Tensión T [N/m]',  'T',     300.0,  6000.0),
        ('Densidad ρ [kg/m²]','rho',  0.15,   0.70),
        ('Altura caja L [m]', 'L',    0.35,   1.20),
        ('Radio base [m]',   'r_bot', 0.04,   0.13),
    ]

    sliders = {}
    for i, (label, key, vmin, vmax) in enumerate(slider_defs):
        ax_s = fig.add_axes([0.12 + i * 0.21, 0.10, 0.16, 0.022],
                            facecolor='#e8e8e8')
        sl = Slider(ax_s, label, vmin, vmax, valinit=p[key], color='steelblue')
        sl.label.set_fontsize(8)
        sl.valtext.set_fontsize(8)
        sliders[key] = sl

    # ── Radio buttons para preset ─────────────────────────────────────────────
    ax_radio = fig.add_axes([0.02, 0.06, 0.08, 0.10], facecolor='#e8e8e8')
    radio = RadioButtons(ax_radio, list(PRESETS.keys()), active=0)
    for label in radio.labels:
        label.set_fontsize(9)

    def on_preset(label):
        preset = PRESETS[label]
        for key, sl in sliders.items():
            sl.set_val(preset[key])
        p.update(preset)
        redraw(fig, axes, p)

    def on_slider(_):
        for key, sl in sliders.items():
            p[key] = sl.val
        p['r_top'] = p['a']   # r_top sigue siendo igual al radio del parche
        redraw(fig, axes, p)

    radio.on_clicked(on_preset)
    for sl in sliders.values():
        sl.on_changed(on_slider)

    # ── Info textual ──────────────────────────────────────────────────────────
    mems   = membrane_modes(p['a'], p['T'], p['rho'])
    shells = shell_modes(p['L'], p['r_bot'])
    info_text = (
        f"Bessel zeros primeros modos:\n"
        f"  (0,1) z=2.405\n"
        f"  (1,1) z=3.832\n"
        f"  (2,1) z=5.136\n"
        f"  (0,2) z=5.520\n\n"
        f"f = z·√(T/ρ) / (2π·a)\n\n"
        f"Caja (cono, abierto-abierto):\n"
        f"  fₙ = n·c / (2·Leff)\n"
        f"  Leff = L + 0.6·r_bot"
    )
    ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes,
                 fontsize=7.5, va='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    redraw(fig, axes, p)
    return fig


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    fig = build_ui('Rum')
    plt.show()
