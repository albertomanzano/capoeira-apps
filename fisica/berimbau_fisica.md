# Física acústica del berimbau

## Estructura del instrumento

El berimbau tiene dos componentes acústicamente activos:

1. **El arame** — cuerda de acero tensa sobre el arco de biriba (verga). Es la fuente de sonido.
2. **La cabaça** — calabazo seco que actúa como resonador. Amplifica selectivamente los armónicos del arame.

A diferencia del atabaque, donde la caja tiene una serie de resonancias armónicas fijas, la cabaça tiene **una sola resonancia de baja frecuencia** (Helmholtz) que el músico modifica en tiempo real.

---

## 1. El arame — cuerda vibrante

### Descripción física

El arame es un hilo de acero de diámetro $d_w \approx 0.8$–$1.0$ mm, longitud $L$ entre los dos extremos del arco, tensado por la curvatura del palo de biriba. La densidad lineal es:

$$\mu = \rho_\text{acero} \cdot \pi \left(\frac{d_w}{2}\right)^2 \approx 7800 \cdot \pi (0.45 \times 10^{-3})^2 \approx 5 \times 10^{-3}\ \text{kg/m}$$

### Ecuación de onda

$$\frac{\partial^2 u}{\partial x^2} = \frac{1}{c_s^2}\frac{\partial^2 u}{\partial t^2}, \qquad c_s = \sqrt{\frac{T}{\mu}}$$

donde $u(x,t)$ es el desplazamiento transversal y $T$ la tensión (N).

### Modos normales

Condiciones de contorno: $u(0,t) = u(L,t) = 0$ (ambos extremos fijos al arco).

$$u_n(x,t) = \sin\!\left(\frac{n\pi x}{L}\right)\cos(\omega_n t), \quad n = 1, 2, 3, \ldots$$

### Frecuencias propias

$$f_n = \frac{n}{2L}\sqrt{\frac{T}{\mu}}, \quad n = 1, 2, 3, \ldots$$

Los sobretonos son **perfectamente armónicos** (múltiplos enteros del fundamental). Esto contrasta con la membrana del atabaque, cuyos sobretonos son inarmónicos (zeros de Bessel).

### Dimensiones por tipo de berimbau

| Tipo | Longitud $L$ | Afinación aprox. | Cabaça |
|:---:|:---:|:---:|:---:|
| Viola | ~150 cm | más agudo | pequeña |
| Médio | ~155 cm | medio | mediana |
| Gunga | ~160 cm | más grave | grande |

### El dobrão

Al presionar el arame con la moneda o piedra a una fracción $\alpha \in (0,1)$ de su longitud, se generan dos segmentos. El que vibra con la cabaça tiene longitud efectiva $L' = (1-\alpha) L$, lo que sube la frecuencia:

$$f_1' = \frac{f_1}{1-\alpha}$$

En la práctica, $\alpha \approx 0.10$–$0.12$, lo que da un intervalo de aproximadamente **un tono entero** entre nota abierta y nota tapada.

---

## 2. La cabaça — resonador de Helmholtz

### Por qué no es una cavidad esférica simple

Una esfera rígida *sin abertura* tiene modos de onda estacionaria cuya frecuencia más baja es $f \approx 0.715\,c/d \sim 1000$–$1500$ Hz para las dimensiones de una cabaça. Pero la cabaça tiene una **boca** (apertura), lo que cambia completamente el mecanismo dominante a bajas frecuencias.

### El mecanismo de Helmholtz

Cuando la longitud de onda del sonido es mucho mayor que las dimensiones de la cavidad ($\lambda \gg d$), la cavidad se comporta como un sistema **masa–muelle concentrado** (lumped):

- **Masa**: el tapón de aire en la boca, de área $A = \pi r^2$ y longitud efectiva $L_\text{ef}$
- **Muelle**: el aire del interior, de volumen $V$ y rigidez neumática $k = \rho c^2 A^2 / V$

La frecuencia de resonancia es:

$$\boxed{f_H = \frac{c}{2\pi}\sqrt{\frac{A}{V \cdot L_\text{ef}}}}$$

donde $c \approx 343$ m/s es la velocidad del sonido en el aire.

### Corrección de extremo

La boca de la cabaça carece de cuello pronunciado ($L_\text{cuello} \approx 0$), por lo que la longitud efectiva se reduce a la corrección de radiación en el extremo libre:

$$L_\text{ef} = L_\text{cuello} + 0.85\, r \approx 0.85\, r$$

(El factor 0.85 corresponde a una apertura circular no embridada; para abertura embridada sería $8r/3\pi \approx 0.849\,r$, prácticamente igual.)

Sustituyendo $A = \pi r^2$:

$$f_H = \frac{c}{2\pi}\sqrt{\frac{\pi r^2}{V \cdot 0.85\, r}} = \frac{c}{2\pi}\sqrt{\frac{\pi r}{0.85\, V}}$$

### Volumen de la cabaça

Para una cabaça aproximadamente esférica de diámetro máximo $d$:

$$V \approx \frac{\pi}{6} d^3$$

Con esta aproximación:

$$f_H \approx \frac{c}{2\pi}\sqrt{\frac{\pi r}{0.85 \cdot \frac{\pi}{6} d^3}} = \frac{c}{2\pi}\sqrt{\frac{6\, r}{0.85\, d^3}}$$

Nótese que $f_H \propto \sqrt{r/d^3}$: la resonancia sube al agrandarse la boca y baja al crecer el diámetro de la cabaça.

### Valores típicos

| Tipo | $d$ (cm) | $V$ (L) | $r_\text{boca}$ (cm) | $f_H$ (Hz) aprox. |
|:---:|:---:|:---:|:---:|:---:|
| Viola | 12 | 0.9 | 2.0 | ~490 |
| Médio | 17 | 2.6 | 3.0 | ~320 |
| Gunga | 22 | 5.6 | 4.0 | ~220 |

La condición de Helmholtz es válida: $\lambda = c/f_H \approx 0.7$–$1.5$ m $\gg d$.

### Comparación con la caja del atabaque

| | Atabaque (caja cónica) | Berimbau (cabaça) |
|---|---|---|
| Modelo | Ecuación de Webster (1D) | Resonador de Helmholtz (0D) |
| Resonancias | Serie $f_n = n c / 2L_\text{ef}$ | Una sola: $f_H$ |
| Origen físico | Onda estacionaria axial | Sistema masa–muelle neumático |
| Variable de diseño | Longitud $L$, radios | Volumen $V$, radio boca $r$ |
| Control músico | Ninguno (estático) | Continuo (vientre) |

---

## 3. El control activo — efecto del vientre

El músico presiona la boca de la cabaça contra su abdomen, variando continuamente la apertura efectiva. Sea $\beta \in [0, 1]$ el grado de apertura ($\beta = 0$: cerrada, $\beta = 1$: abierta):

$$A_\text{ef}(\beta) = \beta \cdot A$$

La frecuencia de Helmholtz se convierte en una función del gesto:

$$f_H(\beta) = \frac{c}{2\pi}\sqrt{\frac{\beta A}{V \cdot L_\text{ef}}} = \beta^{1/2} \cdot f_{H,\text{max}}$$

- $\beta = 0$: la resonancia desaparece (cavidad cerrada)
- $\beta = 1$: resonancia máxima en $f_{H,\text{max}}$
- $\beta$ intermedio: la resonancia barre el espectro del arame

Cuando $f_H(\beta) \approx n \cdot f_1$, el armónico $n$ del arame se acopla fuertemente con la cabaça y se amplifica. Al abrir y cerrar rítmicamente se obtiene el timbre oscilante característico del berimbau.

---

## 4. Acoplamiento arame–cabaça

### Mecanismo

El acoplamiento es **mecánico, no acústico**. La geometría del instrumento es:

$$\text{arame} \longrightarrow \text{biriba} \longrightarrow \text{base de la cabaça} \longrightarrow \text{cuerpo} \longrightarrow \text{boca}$$

La boca apunta en dirección contraria al arame; no hay acoplamiento aéreo directo entre cuerda y cavidad (verificado experimentalmente: interponer material amortiguador entre biriba y cabaça elimina completamente la resonancia; excitar con altavoz externo no produce amplificación apreciable).

El camino de energía es:

1. El arame vibra transversalmente → genera pulsos de tensión en los extremos del biriba.
2. El biriba flexiona → transmite vibraciones mecánicas a la base de la cabaça a través del punto de unión.
3. El cuerpo de la cabaça vibra como carcasa → excita el aire interior.
4. El resonador de Helmholtz amplifica el armónico cuya frecuencia coincide con $f_H$.
5. El sonido amplificado radia por la boca.

La ecuación efectiva del resonador forzado es:

$$\ddot{q} + \frac{\omega_H}{Q}\dot{q} + \omega_H^2\, q = F_n(t)$$

donde $q$ es el caudal de aire en la boca, $\omega_H = 2\pi f_H$, $Q$ es el factor de calidad de la cabaça, y $F_n$ es la fuerza de excitación transmitida mecánicamente por el biriba al $n$-ésimo armónico del arame.

### Condición de acoplamiento fuerte

El acoplamiento es eficiente cuando la frecuencia del armónico coincide con la resonancia:

$$\left|\frac{f_H - n\, f_1}{f_H}\right| < \frac{1}{2Q}$$

Para una cabaça típica, $Q \approx 10$–$30$, lo que da un ancho de banda de acoplamiento de $\sim 3$–$5\%$ de $f_H$.

### Diferencia con el atabaque

En el atabaque, el acoplamiento es entre la membrana (modos de Bessel, inarmónicos) y la caja (armónicos del tubo). El diseño busca alinear estáticamente los picos. En el berimbau, la fuente (arame) es armónica y el resonador (cabaça) tiene un solo pico que el músico mueve dinámicamente — el acoplamiento se activa y desactiva a voluntad.

---

## 5. Medida práctica de la cabaça (luthería)

Para seleccionar o diseñar una biriba a partir de una cabaça dada, hay que conocer su $f_H$. Los únicos parámetros que hay que medir son el **diámetro de la boca** $d_\text{boca}$ y el **volumen interior** $V$.

### Protocolo de medida

**Diámetro de la boca:**
Medir el diámetro interior de la abertura con calibre o regla. De aquí se obtienen $r = d_\text{boca}/2$ y $A = \pi r^2$.

**Volumen interior:**
Llenar la cabaça con arroz, lentejas u otro grano seco. Verter el contenido en una jarra graduada. El volumen leído es directamente el volumen interior de la cabaça — los granos ocupan exactamente el espacio disponible, así que el factor de empaquetamiento no afecta al resultado.

**Cálculo:**

$$f_H = \frac{c}{2\pi}\sqrt{\frac{\pi r}{0.85\, V}}$$

con $c = 343$ m/s, $r$ en metros, $V$ en m³.

### Por qué solo hay dos parámetros independientes

$L_\text{ef}$ no se mide: es la corrección de extremo $L_\text{ef} = 0.85\,r$, calculada directamente del radio de la boca que ya se midió. La cabaça no tiene cuello.

### El orden correcto en luthería

La cabaça tiene $f_H$ **fija** por su geometría — no se puede ajustar sin modificarla físicamente. La biriba, en cambio, permite ajustar $f_1$ variando longitud y curvatura. Por eso el proceso natural es:

1. Medir la cabaça → obtener $f_H$
2. Identificar a qué armónico del arame debe corresponder: $f_H = n \cdot f_1$
3. Seleccionar/diseñar la biriba para que $f_1$ encaje

### Ajuste fino

La fórmula asume geometría ideal. En la práctica conviene verificar la resonancia excitando la cabaça con una señal de audio de frecuencia variable y detectando el máximo de amplificación de oído. Ver [estructura de la app de luthería](app_lutheria.md).

---

## 6. Caracterización de la biriba (luthería)

### Modelo de rigidez

La biriba quiere volver a su posición recta. El arame, al conectar sus dos extremos, la mantiene arqueada. En equilibrio, la tensión del arame es proporcional a la deformación del palo:

$$T = k(L_0 - L)$$

donde $L_0$ es la longitud del palo recto (natural) y $L$ es la longitud de cuerda entre los dos puntos de anclaje del arame cuando está montado. $k$ es la rigidez de la biriba (N/m).

La frecuencia fundamental resulta:

$$f_1(L) = \frac{1}{2L}\sqrt{\frac{k(L_0 - L)}{\mu}}$$

Al arquear más: $L$ baja y $T$ sube, ambos efectos elevan $f_1$ en la misma dirección.

### Protocolo de medida

**$L_0$:** medir la biriba en reposo (recta) con cinta métrica.

**$L$:** medir la distancia en línea recta entre los dos puntos de anclaje del arame una vez montado. En la práctica equivale a medir la longitud del arame, que es un cable recto bajo tensión.

**$k$:** percutir el arame con el palo en posición de toque → el analizador da $f_1$. Despejar:

$$k = \frac{\mu\,(2 L f_1)^2}{L_0 - L}$$

Con $L_0$, $L$ (cinta métrica) y $f_1$ (espectro), $k$ queda determinada con una sola medida.

### Rango de frecuencias de la biriba

Con $k$ y $L_0$ conocidos, la curva $f_1(L)$ define el espacio completo de frecuencias alcanzables variando la curvatura. Esto permite responder: **¿qué rango de cabaças acepta esta biriba?**

La curva tiene un máximo en $L^* = \frac{2}{3}L_0$, aunque en la práctica el límite lo impone la resistencia mecánica del palo antes de llegar a esa curvatura.

### Uso como herramienta de selección

Caracterizando varias biribas con sus respectivas curvas $f_1(L)$, se puede seleccionar directamente cuál encaja con una cabaça dada (cuya $f_H$ ya se conoce), sin necesidad de montar y probar cada combinación.

---

## 7. Resumen de parámetros

| Parámetro | Símbolo | Efecto principal |
|:---:|:---:|:---|
| Longitud del arame | $L$ | Determina todas las frecuencias ($f \propto 1/L$) |
| Tensión del arame | $T$ | Sube o baja todas las frecuencias ($f \propto \sqrt{T}$) |
| Diámetro del hilo | $d_w$ | Afecta $\mu$ y por tanto $f$ ($f \propto 1/d_w$) |
| Posición del dobrão | $\alpha$ | Nueva longitud efectiva $L' = (1-\alpha)L$ |
| Volumen cabaça | $V$ | Baja $f_H$ al aumentar ($f_H \propto V^{-1/2}$) |
| Radio boca | $r$ | Sube $f_H$ al aumentar ($f_H \propto r^{1/2}$) |
| Apertura vientre | $\beta$ | Controla $f_H$ en tiempo real ($f_H \propto \beta^{1/2}$) |
