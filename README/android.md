# Build Android

Todo lo necesario para compilar y desplegar la [app de luthería](lutheria.md) en Android. Para los quirks de la API de Flet ver [flet.md](flet.md).

## Build

```bash
cd luteria_app
source ../atabaque_venv/bin/activate
rm -f build/.hash/package          # forzar reinstalación de paquetes
flet build apk --module-name app   # entry point es app.py, no main.py
```

APK resultante: `build/flutter/build/app/outputs/flutter-apk/app-release.apk`

```bash
adb install -r build/flutter/build/app/outputs/flutter-apk/app-release.apk
adb logcat | grep -i "python\|flet\|luteria"
```

## Dependencias Android — reglas (`pyproject.toml`)

- Usar `[project] dependencies = [...]` — flet ignora `[tool.flet.dependencies]`
- Sin `scipy` (sin wheels Android) → usar `numpy.fft.rfft` y `rfftfreq`
- Declarar `certifi` explícitamente aunque sea transitivo
- `sounddevice` pendiente de verificar (depende de PortAudio)

## Algoritmo cabaca_search — búsqueda iterativa de f_H

Basado en la [física de la cabaça](fisica.md). Función de transferencia H1 (altavoz→micrófono) en dos fases:

1. **Barrido amplio** (6 sweeps, 100–800 Hz, chirp 4s): acumula Sxy/Sxx/Syy, calcula H1 y coherencia γ², extrae hasta 2 candidatos por score = H1_norm × γ² con separación mínima 50 Hz
2. **Zoom** (10 sweeps, ±60 Hz alrededor de cada candidato, chirp 2s): refina; gana el candidato con mayor coherencia × H1

Parámetros: `COH_MIN=0.5`, `WARMUP=0.3s`. La vista llama `sweep_h1_once` en executor (no bloqueante).
