# App de luthería

App descargable desde `/members/descargas/` en la [web](web.md). Mide y casa cabaças con biribas usando modelos acústicos basados en la [física del berimbau](berimbau_fisica.md) y del [atabaque](atabaque_fisica.md).

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
- Build APK final y prueba en dispositivo tras los últimos cambios de estilo

**Completado**:
- Sounddevice funciona en Android (verificado en dispositivo)
- Icono: logo CCL (`assets/icon.png`, 1024×1024, convertido desde `web_colectivo/src/lib/assets/logo.svg` con cairosvg)
- Estilo: paleta crema/marrón de la web (ThemeMode.LIGHT, mismas variables CSS que [paleta.md](paleta.md))
- Pestañas con esquinas redondeadas (`border_radius=8`)
- Vista "Casar" descartada

## Build Android

Ver [android.md](android.md) para comandos de build y reglas de dependencias, y [flet.md](flet.md) para quirks de la API.
