# Tracking: App de luthería

## Estado general
En desarrollo activo. Stack: Python + Flet 0.84.0 + sounddevice + numpy.

## Estructura de navegación actual
```
NavigationBar (3 pestañas):
├── Instrumentos
│   ├── Cabaça      — views/cabacas.py
│   ├── Biriba      — views/biribas.py
│   └── Casar       — placeholder "en construcción"
├── Biblioteca      — views/biblioteca.py
└── Herramientas
    ├── Tono        — views/tono.py
    └── Espectro    — views/espectro.py
```

## Completado
- `views/cabacas.py`: estimación por dimensiones (V + d → f_H) + medición acústica (barrido H1 iterativo) + guardar en biblioteca
- `views/biribas.py`: inputs L₀/L + selector de arame → percusión → k + curva f₁(L) con notas en eje Y + guardar en biblioteca
- `views/tono.py`: generador sinusoidal con slider, actualizable mientras suena
- `views/espectro.py`: grabación 3s → FFT → series armónicas con colores e intensidad por peso
- `views/biblioteca.py`: tres secciones (Arames / Cabaças / Biribas) con edición y borrado inline
- `views/instrumentos.py`: contenedor con pestañas Cabaça / Biriba / Casar
- `views/herramientas.py`: contenedor con pestañas Tono / Espectro
- `audio/cabaca_search.py`: algoritmo H1 en dos fases (barrido amplio + zoom)
- `audio/espectro.py`: FFT, detect_f1, record_audio
- `audio/android_audio.py`: módulo de audio para Android
- `models/cabaca.py`, `models/biriba.py`, `models/biblioteca.py`: modelos físicos + persistencia local

## Pendiente
- [ ] Vista **Casar**: matching cabaça ↔ biriba con superposición de curvas f₁(L) + f_H
- [ ] Verificar `sounddevice` en Android (depende de PortAudio)
- [ ] Build APK final y prueba en dispositivo real

## Build para Android
```bash
cd luteria_app
source ../atabaque_venv/bin/activate
rm -f build/.hash/package
flet build apk --module-name app
```
APK: `build/flutter/build/app/outputs/flutter-apk/app-release.apk`

## Link de descarga
El APK se ofrecerá desde la web del Colectivo. Ver `tracking/web_colectivo.md`.
