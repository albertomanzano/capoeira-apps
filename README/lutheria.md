# App de luthería

App descargable desde `/members/descargas/` en la [web](web.md). Mide y casa cabaças con biribas usando modelos acústicos basados en la [física del berimbau](fisica.md).

Stack: Python + Flet 0.84.0 + sounddevice + numpy.
Virtualenv: `atabaque_venv/` (raíz del proyecto). Ver [convenciones](convenciones.md).
Ejecutar: `cd luteria_app && python app.py`

## Estructura

```
luteria_app/
├── models/
│   ├── cabaca.py      — clase Cabaca, freq_to_note (solfeo)
│   ├── biriba.py      — clase Biriba, cálculo k, curva f1(L)
│   └── biblioteca.py  — persistencia local
├── audio/
│   ├── tono.py        — TonePlayer + generate_chirp
│   ├── espectro.py    — FFT, find_peaks, plot_spectrum
│   ├── cabaca_search.py — búsqueda iterativa H1 (ver android.md)
│   └── android_audio.py
├── views/
│   ├── cabacas.py     — COMPLETO
│   ├── biribas.py     — COMPLETO
│   ├── biblioteca.py  — COMPLETO
│   ├── tono.py        — COMPLETO
│   ├── espectro.py    — COMPLETO
│   └── instrumentos.py, herramientas.py — contenedores de pestañas
└── app.py             — navegación + NavigationBar
```

## Estado

**Completo**: cabaças (calcular + medir resonancia), biribas (k + curva f₁(L)), biblioteca (arames/cabaças/biribas), tono, espectro.

**Pendiente**:
- Vista "Casar": matching cabaça ↔ biriba con superposición de curvas f₁(L) + f_H
- Verificar sounddevice en Android (depende de PortAudio)
- Build APK final y prueba en dispositivo

## Build Android

Ver [android.md](android.md) para comandos de build y reglas de dependencias, y [flet.md](flet.md) para quirks de la API.
