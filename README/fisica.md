# Física de los instrumentos

Base teórica de la [app de luthería](lutheria.md). Documentación completa en `fisica/atabaque_fisica.md` y `fisica/berimbau_fisica.md`.

## Berimbau — arame (cuerda)

Serie armónica: $f_n = \frac{n}{2L}\sqrt{T/\mu}$

$L$ y $T$ están acoplados: $T = k(L - L_0)$ donde $k$ es la rigidez de la biriba. Más curvatura → L más corto y T mayor → frecuencia sube siempre.

## Berimbau — cabaça (resonador de Helmholtz)

Una sola resonancia dominante: $f_H = \frac{c}{2\pi}\sqrt{\frac{\pi r}{0.85\,V}}$

Solo dos parámetros a medir: $V$ (volumen, por desplazamiento de arroz) y $d$ (diámetro de la boca, con calibre o regla).

## Luthería — proceso

1. Medir cabaça → $f_H$ fija
2. Caracterizar biriba: medir $L_0$ (palo recto) y $L$ (montado), percutir → $f_1$ → calcular $k$
3. Con $k$ y $L_0$ trazar curva $f_1(L)$ y encontrar el rango de cabaças compatibles

El "casar" cabaça ↔ biriba es superponer la curva $f_1(L)$ de la biriba con la $f_H$ de la cabaça. Ver pendiente en [lutheria.md](lutheria.md).

## Atabaque

Física completa en `fisica/atabaque_fisica.md`: membrana circular, caja cónica, acoplamiento.
Modelo interactivo con presets (Rum, Rumpi, Lê): `fisica/atabaque_model.py` — ejecutar con `atabaque_venv` activo (ver [convenciones](convenciones.md)).

La derivación completa del berimbau está en `fisica/berimbau_fisica.md`.
