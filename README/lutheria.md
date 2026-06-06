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
- Prueba en dispositivo del APK v1.1

**Completado**:
- Build APK v1.1 ✓ (2026-06-06) — release en GitHub: `v1.1-luteria`
- Sounddevice funciona en Android (verificado en dispositivo)
- Icono: logo CCL (`assets/icon.png`, 1024×1024, convertido desde `web_colectivo/src/lib/assets/logo.svg` con cairosvg)
- Estilo: paleta crema/marrón de la web (ThemeMode.LIGHT, mismas variables CSS que [paleta.md](paleta.md))
- Pestañas con esquinas redondeadas (`border_radius=8`)
- Vista "Casar" descartada

## Releases

Los APKs se publican como GitHub Releases en `albertomanzano/capoeira-apps`. La URL del release activo se configura en `web_colectivo/src/routes/members/descargas/+page.svelte`.

| Versión | Tag | Fecha | Novedades |
|---|---|---|---|
| v1.1 | `v1.1-luteria` | 2026-06-06 | Paleta crema/marrón, icono CCL, esquinas redondeadas, sin vista Casar |
| v1.0 | `v1.0-luteria` | 2026-06-01 | Primera release |

Para crear un nuevo release:
```bash
# 1. Compilar
cd luteria_app && source ../atabaque_venv/bin/activate
flet build apk --module-name app
cp build/flutter/build/app/outputs/flutter-apk/app-release.apk build/apk/lutheria.apk

# 2. Publicar en GitHub
gh release create vX.Y-luteria --repo albertomanzano/capoeira-apps \
  --title "Luthería vX.Y" --notes "..." \
  luteria_app/build/apk/lutheria.apk

# 3. Actualizar la constante LUTERIA_APK en descargas/+page.svelte y hacer deploy web
```

## Build Android

Ver [android.md](android.md) para comandos de build y reglas de dependencias, y [flet.md](flet.md) para quirks de la API.
