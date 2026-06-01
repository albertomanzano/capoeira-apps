# Proyecto: apps de capoeira

## Qué es esto

Tres líneas de trabajo:

1. **App de luthería** — modelado físico y computacional de los instrumentos de percusión y cuerda de la capoeira (atabaque, berimbau). Modelos Python interactivos y app para medir y casar cabaças con biribas.

2. **App de entrenamiento físico** — gestión del físico de las clases de capoeira: registro de alumnos, marcas por ejercicio, árbol de habilidades y progreso individual. App nativa Android (`entrenamiento_app/`) con Flet + Supabase. Timer con audio en background.

3. **Web del Colectivo** — web pública del colectivo que integra login de alumnos para ver sus stats de entrenamiento y link de descarga de la app de luthería.

## Tracking por proyecto

- `tracking/luteria.md` — estado y pendientes de la app de luthería
- `tracking/entrenamiento_app.md` — estado y pendientes de la app de entrenamiento (Flet/Android)
- `tracking/web_colectivo.md` — web del Colectivo (en standby; futuro: página pública + links APK)

## Estado actual

### Física de instrumentos — `fisica/`
- `fisica/atabaque_fisica.md`: física completa del atabaque (membrana circular, caja cónica, acoplamiento)
- `fisica/atabaque_model.py`: modelo interactivo con sliders y visualización (matplotlib/Qt5Agg)
  - Presets: Rum, Rumpi, Lê
  - Ejecutar: activar `atabaque_venv` y correr `python fisica/atabaque_model.py`
- `fisica/berimbau_fisica.md`: física completa incluyendo luthería (secciones 5 y 6)
- `fisica/app_lutheria.md`: estructura completa de la app de luthería
- Modelo Python berimbau: **pendiente**

### App de luthería — `luteria_app/` — en desarrollo
- Stack: Python + Flet 0.84.0 + sounddevice + matplotlib (para plots embebidos como PNG)
- Virtualenv: `atabaque_venv/` (matplotlib, numpy, flet, sounddevice, scipy)
- Ejecutar: `cd luteria_app && python app.py`

#### Estructura de la app
```
luteria_app/
├── models/
│   ├── cabaca.py     — clase Cabaca, función freq_to_note (solfeo: Do/Re/Mi...)
│   ├── biriba.py     — clase Biriba, cálculo de k y curva f1(L)
│   └── biblioteca.py — persistencia local (arames, cabaças, biribas)
├── audio/
│   ├── tono.py       — TonePlayer + generate_chirp(f_min, f_max, duration)
│   ├── espectro.py   — FFT, find_peaks, find_harmonic_groups, plot_spectrum
│   ├── cabaca_search.py — búsqueda iterativa H1: sweep_h1_once, find_candidates, zoom_winner
│   └── android_audio.py — módulo de audio para Android
├── views/
│   ├── instrumentos.py — contenedor pestañas Cabaça / Biriba / Casar
│   ├── cabacas.py    — COMPLETO: estimación por dimensiones + medición acústica
│   ├── biribas.py    — COMPLETO: L₀/L + selector arame → k + curva f₁(L) + guardar
│   ├── biblioteca.py — COMPLETO: Arames / Cabaças / Biribas con edición y borrado
│   ├── herramientas.py — contenedor pestañas Tono / Espectro
│   ├── tono.py       — COMPLETO: generador de tono sinusoidal con slider
│   └── espectro.py   — COMPLETO: analizador de espectro por micrófono
└── app.py            — navegación principal con NavigationBar
```
#### Vistas completadas
- `views/cabacas.py`: dos secciones:
  - **Calcular**: V + d → f_H teórica (Hz + nota solfeo) + guardar en biblioteca
  - **Medir resonancia**: barrido acústico iterativo → f_H medida + comparación vs. teórica en cents + guardar
- `views/biribas.py`: inputs L₀/L + selector de arame → percusión → k + curva f₁(L) con notas en eje Y + guardar en biblioteca
- `views/biblioteca.py`: tres secciones (Arames / Cabaças / Biribas) con edición y borrado inline
- `views/tono.py`: generador sinusoidal con slider, actualizable mientras suena
- `views/espectro.py`: grabación 3s → FFT → series armónicas con colores e intensidad por peso

#### Build para Android

```bash
cd luteria_app
source ../atabaque_venv/bin/activate
rm -f build/.hash/package          # forzar reinstalación de paquetes
flet build apk --module-name app   # entry point es app.py, no main.py
```

APK resultante: `build/flutter/build/app/outputs/flutter-apk/app-release.apk`

Instalar y depurar por USB (ADB):
```bash
adb install -r build/flutter/build/app/outputs/flutter-apk/app-release.apk
adb logcat | grep -i "python\|flet\|luteria"
```

#### Módulo `audio/cabaca_search.py` — búsqueda iterativa de f_H

Algoritmo H1 (función de transferencia altavoz→micrófono) en dos fases:

1. **Barrido amplio** (N_BROAD=6 sweeps, 100–800 Hz, chirp 4s): acumula Sxy/Sxx/Syy, calcula H1 y coherencia γ², extrae hasta N_CANDS=2 candidatos por score = H1_norm × γ² con separación mínima 50 Hz
2. **Zoom** (N_ZOOM=10 sweeps, ±60 Hz alrededor de cada candidato, chirp 2s): refina; gana el candidato con mayor coherencia × H1 en el pico

Funciones exportadas: `sweep_h1_once(chirp_out)`, `accumulate`, `finalize`, `find_candidates`, `zoom_winner`

Parámetros clave: `COH_MIN=0.5` (umbral coherencia), `WARMUP=0.3s` (trim al inicio del playrec)

La vista llama `sweep_h1_once` en executor sweep a sweep (no bloqueante), actualizando la UI entre cada pasada. El botón Medir/Detener usa una flag `_running[0]` comprobada entre sweeps.

**Reglas de dependencias para Android** (`luteria_app/pyproject.toml`):
- Usar `[project] dependencies = [...]` — flet ignora `[tool.flet.dependencies]`
- `scipy` no tiene wheels Android — reemplazar con `numpy` (mismas funciones FFT: `numpy.fft.rfft`, `rfftfreq`)
- `certifi` hay que declararlo explícitamente aunque sea transitivo
- `sounddevice` pendiente de verificar en Android (depende de PortAudio)

#### Pendiente
- **Casar**: matching cabaça ↔ biriba con superposición de curvas f₁(L) + f_H
- Verificar `sounddevice` en Android (depende de PortAudio)
- Build APK final y prueba en dispositivo real

#### Notas de API Flet 0.84.0 (errores ya resueltos)
- `Tab` usa `label=` no `text=`
- `ColorScheme` no acepta `background=`
- `ft.alignment.Alignment(0,0)` (no `ft.alignment.center`)
- `ft.BoxFit.CONTAIN` (no `ft.ImageFit`)
- `ft.Icons.X` mayúsculas (no `ft.icons.X`)
- `ElevatedButton(content=ft.Text(...))` (no `text=`)
- `scroll=` en `ft.Column`, no en `ft.Container`
- `ft.Image` requiere `src` obligatorio — no instanciar sin él
- `NavigationBar` + switching manual (no `ft.Tabs` con lista)
- Threading: `async def main` + `page.run_task()` + `run_in_executor` — `threading.Thread` no hace flush de `page.update()`

## Física del berimbau (resumen)

**Arame (cuerda 1D)**
- Serie armónica: $f_n = \frac{n}{2L}\sqrt{T/\mu}$
- $L$ y $T$ acoplados: $T = k(L_0 - L)$ donde $k$ es rigidez de la biriba
- Más curvatura → L más corto y T mayor → frecuencia sube siempre

**Cabaça (resonador de Helmholtz)**
- Una sola resonancia: $f_H = \frac{c}{2\pi}\sqrt{\frac{\pi r}{0.85\,V}}$
- Solo dos parámetros a medir: $V$ (arroz+jarra) y $d$ (calibre/regla)

**Luthería**
- Proceso inverso: medir cabaça primero (f_H fija), luego ajustar biriba
- Biriba caracterizada por $k$: medir $L_0$ (palo recto), $L$ (palo montado), percutir → $f_1$ → $k$
- Con $k$ y $L_0$ se traza la curva $f_1(L)$ y el rango de cabaças compatibles

---

## Convenciones

- Documentos de física en Markdown con LaTeX
- Notas musicales en solfeo (Do, Re, Mi, Fa, Sol, La, Si), no notación anglosajona
- Virtualenv compartido en `atabaque_venv/` (raíz del proyecto)
- Sin comentarios en el código salvo que el motivo no sea obvio
