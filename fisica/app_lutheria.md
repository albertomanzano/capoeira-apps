# App de luthería — documentación

App móvil para medir, registrar y cruzar los instrumentos del berimbau (cabaças, biribas, arames). Stack: Python + Flet 0.84.0 + numpy + matplotlib (plots como PNG en memoria). Virtualenv: `atabaque_venv/`.

---

## Estructura de navegación

```
NavigationBar (3 pestañas principales)
├── Instrumentos      → sub-tabs: Cabaça | Biriba | Casar
├── Biblioteca        → arames / cabaças / biribas guardadas (CRUD)
└── Herramientas      → sub-tabs: Tono | Espectro
```

`app.py` instancia las tres vistas y gestiona el switching con `NavigationBar`. Al navegar a Biblioteca se llama `biblioteca_refresh()` para recargar los datos del JSON.

---

## Árbol de ficheros

```
lutheria_app/
├── app.py
├── pyproject.toml
├── audio/
│   ├── android_audio.py   — AndroidTonePlayer, android_record_audio, MicPermissionError
│   └── espectro.py        — process_and_plot, record_audio, find_peaks, find_harmonic_groups
├── models/
│   ├── cabaca.py          — clase Cabaca, freq_to_note (solfeo con octava y cents)
│   ├── biriba.py          — clase Biriba: calcula k y curva f₁(L)
│   └── biblioteca.py      — persistencia JSON: arames / cabaças / biribas
└── views/
    ├── __init__.py
    ├── instrumentos.py    — contenedor con sub-tabs Cabaça / Biriba / Casar
    ├── cabacas.py         — estimación f_H por dimensiones + guardado
    ├── biribas.py         — L₀/L/arame + percusión → k + curva + guardado
    ├── biblioteca.py      — lista y CRUD de arames/cabaças/biribas
    ├── herramientas.py    — contenedor con sub-tabs Tono / Espectro
    ├── tono.py            — generador sinusoidal con slider
    └── espectro.py        — analizador espectral (grabación → FFT → plot)
```

---

## Pestaña Instrumentos

Tres sub-tabs con tab-bar manual (Containers con on_click, sin ft.Tabs).

### Sub-tab Cabaça (`views/cabacas.py`) — COMPLETO

**Flujo:**
1. Usuario introduce V (ml) y d (mm)
2. Modelo `Cabaca` calcula $f_H = \frac{c}{2\pi}\sqrt{\frac{\pi r}{0.85\,V}}$
3. Muestra Hz + nota en solfeo con octava y cents
4. Campo nombre → botón Guardar → persiste en `biblioteca.json`

**Modelo:** `models/cabaca.py → Cabaca`, `freq_to_note`

### Sub-tab Biriba (`views/biribas.py`) — COMPLETO

**Flujo:**
1. Usuario introduce L₀ (cm), L (cm) y selecciona arame del desplegable
2. Botón "Medir percusión" → graba 3s → `detect_f1` detecta la fundamental
3. `Biriba._calc_k` → $k = \mu(2Lf_1)^2 / (L_0 - L)$
4. Plot matplotlib de la curva $f_1(L)$ con notas en el eje Y derecho y punto medido marcado
5. Campo nombre → botón Guardar → persiste en `biblioteca.json`

**Modelo:** `models/biriba.py → Biriba`, `models/biblioteca.py → add_biriba, get_arames`

El desplegable de arames se carga de la biblioteca (con defaults START 0.8mm / 1.0mm si está vacía). El botón de recarga (⟳) refresca la lista sin reiniciar la vista.

### Sub-tab Casar (`views/instrumentos.py → _casar_placeholder`) — PENDIENTE

Placeholder. Diseño previsto: seleccionar cabaça + biriba de la biblioteca, superponer $f_H$ sobre la curva $f_1(L)$, mostrar el punto de cruce o la distancia al rango.

---

## Pestaña Biblioteca (`views/biblioteca.py`) — COMPLETO

Lista arames, cabaças y biribas guardadas. Cada card tiene botones de edición (diálogo `AlertDialog`) y borrado. Al navegar a esta pestaña se llama `refresh()` para releer el JSON.

**Secciones:** ARAMES → CABAÇAS → BIRIBAS (scroll vertical único)

**CRUD disponible:**
- Arames: nombre, marca, calibre, μ (g/m), material
- Cabaças: nombre, f_H, V_ml, d_mm
- Biribas: nombre, k, L₀, L, calibre, f₁ medida

**Persistencia:** `models/biblioteca.py` → `biblioteca.json` en `FLET_APP_STORAGE_DATA` (Android) o `~` (desktop).

---

## Pestaña Herramientas

### Sub-tab Tono (`views/tono.py`) — COMPLETO, funciona en Android

Genera un tono sinusoidal continuo. Slider 50–1000 Hz. En Android usa `AndroidTonePlayer` (AudioTrack MODE_STREAM, WRITE_BLOCKING, chunks de 2048 muestras vía `ByteBuffer.wrap(bytearray)`).

### Sub-tab Espectro (`views/espectro.py`) — COMPLETO con bug en Android

Graba 3 s → FFT → detecta picos → agrupa en series armónicas → plot matplotlib.

**Pipeline (`audio/espectro.py`):**
1. `record_audio` → `android_record_audio` (Android) o sounddevice (desktop)
2. Ventana Hanning + rfft
3. `find_peaks`: top-10 picos en 50–1200 Hz, threshold 4% del máximo
4. `find_harmonic_groups`: agrupa por f₀ con tolerancia 4% en ratio n
5. `weights`: reparte energía entre series y entre picos de cada serie
6. `plot_spectrum`: curva + líneas verticales coloreadas por serie + etiquetas nota/Hz/%

**Output UI:**
- Tarjeta "TONO FUNDAMENTAL" con nota grande y Hz
- Plot PNG embebido
- Lista de series con picos, notas y porcentaje de energía

**Bug conocido (solo Android):** el analizador muestra "Error: float division by zero" tras grabar. Ver sección de bugs.

---

## Modelos

### `models/cabaca.py`

```python
class Cabaca(name, V_ml, d_mm, f_H_measured=None)
    .f_H     → Hz (calculado o medido)
    .note    → str (solfeo)

freq_to_note(freq) → "Do#4 (+12c)"   # nota, octava, desviación en cents
```

### `models/biriba.py`

```python
class Biriba(name, L0_cm, L_cm, calibre=None, f1_measured=0.0, mu=None)
    .k           → N/m  (rigidez de la biriba)
    .f1_at(L_m)  → Hz   (frecuencia fundamental a longitud L)
    .freq_range() → (L_vals, freqs)  (curva completa para el plot)
```

`mu` puede pasarse directamente (float kg/m) o se infiere de `calibre` vía `WIRE_MU`.

### `models/biblioteca.py`

JSON en una ruta writable. API: `get_arames / add_arame / update_arame / delete_arame` y equivalentes para `cabacas` y `biribas`. Los arames tienen defaults START 0.8mm y 1.0mm (acero EN 10270-1, densidad 7850 kg/m³).

---

## Audio Android (`audio/android_audio.py`)

Solo usa `autoclass` de pyjnius. `jarray`, `jshort`, `jint` no están disponibles en el build.

### `AndroidTonePlayer`

AudioTrack en modo STREAM. Thread daemon que alimenta chunks de 2048 muestras int16. `ByteBuffer.wrap(bytearray(samples.tobytes()))` para pasar datos Python → Java.

### `android_record_audio() → np.ndarray`

AudioRecord PCM_16BIT mono 44100 Hz. `ByteBuffer.allocateDirect` (obligatorio; `allocate` heap es rechazado por AudioRecord). `FileChannel.write(ByteBuffer)` para copiar Java→Java sin iterar en Python. Lee el PCM con `np.fromfile` y normaliza a float32 en [-1, 1].

### `_check_mic_permission()`

Usa `ActivityThread.currentApplication().getApplicationContext()`. Lanza `MicPermissionError` si no hay permiso RECORD_AUDIO.

---

## Build Android

```bash
cd lutheria_app
source ../atabaque_venv/bin/activate
rm -f build/.hash/package          # forzar reinstalación de paquetes pip
flet build apk --module-name app   # entry point: app.py, no main.py
```

APK: `build/flutter/build/app/outputs/flutter-apk/app-release.apk`

```bash
adb install -r build/flutter/build/app/outputs/flutter-apk/app-release.apk
adb logcat | grep -i "python\|flet\|luteria\|traceback\|error"
```

**Reglas críticas `pyproject.toml`:**
- Usar `[project] dependencies` — flet ignora `[tool.flet.dependencies]`
- Incluir `flet==0.84.0` explícitamente (con `[project]` no se añade solo)
- `scipy` no tiene wheels Android → reemplazado por `numpy.fft`
- `certifi` hay que declararlo aunque sea transitivo
- `sounddevice` con `try/except` en el import de módulo (PortAudio no disponible en Android)

**`rm -f build/.hash/package`:** solo afecta a paquetes pip; los fuentes Python siempre se repaquetan.

---

## Notas API Flet 0.84.0

- `ft.BoxFit.CONTAIN` (no `ft.ImageFit`)
- `ft.alignment.Alignment(0, 0)` (no `ft.alignment.center`)
- `ft.Icons.X` en mayúsculas (no `ft.icons.X`)
- `ElevatedButton(content=ft.Text(...))` (no `text=`)
- `scroll=ft.ScrollMode.AUTO` va en `ft.Column`, no en `ft.Container`
- `ft.Image(src=...)` requiere `src` obligatorio
- Navegación: `NavigationBar` + switching manual de `content.content`
- Threading: `async def main` + `page.run_task()` + `run_in_executor` — `threading.Thread` no hace flush de `page.update()`
- `ft.SafeArea` alrededor del Column principal elimina solapamiento con la barra de estado Android

---

## Bugs conocidos

### "float division by zero" en Espectro (solo Android)

**Síntoma:** tras grabar 3 s, el analizador muestra "Error: float division by zero".

**Diagnóstico probable:** matplotlib auto-scaling sobre un espectro con magnitudes nulas o casi nulas en el rango 50–1200 Hz. Cuando `m_plot.max() == 0`, el eje Y queda en rango [0, 0] y matplotlib intenta dividir por ese rango para calcular los ticks → `ZeroDivisionError: float division by zero`. En desktop hay suficiente ruido de fondo para que esto no ocurra.

**Fix aplicado (pendiente de verificar en Android):** guardia en `plot_spectrum` con `ax.set_ylim` explícito, y `traceback.print_exc()` en el handler de error de `views/espectro.py` para capturar el traceback completo en logcat.

**Para verificar:** `adb logcat | grep -i "traceback\|zero\|error\|python"` mientras se reproduce el error.
