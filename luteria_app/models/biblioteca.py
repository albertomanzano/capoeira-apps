import json
import math
import os
from datetime import date

_PATH = os.path.join(
    os.environ.get("FLET_APP_STORAGE_DATA") or os.path.expanduser("~"),
    "biblioteca.json",
)

_RHO_START = 7850  # kg/m³  — acero EN 10270-1 (cuerda de piano), marca START

DEFAULT_ARAMES = [
    {
        'name': 'START 0.8mm',
        'brand': 'START',
        'calibre': '0.8mm',
        'mu': round(_RHO_START * math.pi * (0.4e-3) ** 2, 7),  # 3.9479e-3 kg/m
        'material': 'Acero EN 10270-1',
        'date': '2026-04-30',
    },
    {
        'name': 'START 1.0mm',
        'brand': 'START',
        'calibre': '1.0mm',
        'mu': round(_RHO_START * math.pi * (0.5e-3) ** 2, 7),  # 6.1685e-3 kg/m
        'material': 'Acero EN 10270-1',
        'date': '2026-04-30',
    },
]


def _load() -> dict:
    if not os.path.exists(_PATH):
        return {'cabacas': [], 'biribas': [], 'arames': []}
    with open(_PATH, encoding='utf-8') as f:
        data = json.load(f)
    data.setdefault('cabacas', [])
    data.setdefault('biribas', [])
    data.setdefault('arames', [])
    return data


def _save(data: dict):
    with open(_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── arames ────────────────────────────────────────────────────────────────────

def get_arames() -> list[dict]:
    data = _load()
    if not data['arames']:
        data['arames'] = DEFAULT_ARAMES
        _save(data)
    return data['arames']


def add_arame(name: str, brand: str, calibre: str, mu: float, material: str = ''):
    data = _load()
    data['arames'].append({
        'name': name,
        'brand': brand,
        'calibre': calibre,
        'mu': round(mu, 7),
        'material': material,
        'date': str(date.today()),
    })
    _save(data)


def update_arame(idx: int, **fields):
    data = _load()
    data['arames'][idx].update(fields)
    _save(data)


def delete_arame(idx: int):
    data = _load()
    data['arames'].pop(idx)
    _save(data)


# ── cabacas ───────────────────────────────────────────────────────────────────

def get_cabacas() -> list[dict]:
    return _load()['cabacas']


def add_cabaca(name: str, f_H: float, V_ml: float, d_mm: float):
    data = _load()
    data['cabacas'].append({
        'name': name,
        'f_H': round(f_H, 2),
        'V_ml': V_ml,
        'd_mm': d_mm,
        'date': str(date.today()),
    })
    _save(data)


def update_cabaca(idx: int, **fields):
    data = _load()
    data['cabacas'][idx].update(fields)
    _save(data)


def delete_cabaca(idx: int):
    data = _load()
    data['cabacas'].pop(idx)
    _save(data)


# ── biribas ───────────────────────────────────────────────────────────────────

def get_biribas() -> list[dict]:
    return _load()['biribas']


def add_biriba(name: str, k: float, L0_cm: float, L_cm: float,
               calibre: str, f1_measured: float,
               mu: float = None, arame_name: str = None):
    data = _load()
    entry = {
        'name': name,
        'k': round(k, 1),
        'L0_cm': L0_cm,
        'L_cm': L_cm,
        'calibre': calibre,
        'f1_measured': round(f1_measured, 2),
        'date': str(date.today()),
    }
    if mu is not None:
        entry['mu'] = round(mu, 7)
    if arame_name is not None:
        entry['arame_name'] = arame_name
    data['biribas'].append(entry)
    _save(data)


def update_biriba(idx: int, **fields):
    data = _load()
    data['biribas'][idx].update(fields)
    _save(data)


def delete_biriba(idx: int):
    data = _load()
    data['biribas'].pop(idx)
    _save(data)
