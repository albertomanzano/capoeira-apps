# Física acústica del atabaque / congas

## 1. El parche — membrana circular

### Descripción física

El parche es una membrana circular de radio $a$, tensada uniformemente con tensión $T$ (N/m) y densidad superficial $\rho$ (kg/m²). Al golpearla, vibra formando ondas estacionarias bidimensionales.

### Ecuación de onda

$$\nabla^2 u = \frac{1}{c_m^2} \frac{\partial^2 u}{\partial t^2}$$

donde $u(r, \theta, t)$ es el desplazamiento vertical y $c_m = \sqrt{T/\rho}$ es la velocidad de onda en la membrana.

En coordenadas polares:

$$\frac{1}{r}\frac{\partial}{\partial r}\left(r \frac{\partial u}{\partial r}\right) + \frac{1}{r^2}\frac{\partial^2 u}{\partial \theta^2} = \frac{1}{c_m^2}\frac{\partial^2 u}{\partial t^2}$$

### Solución: modos normales

Separando variables $u(r, \theta, t) = R(r) \cdot \Theta(\theta) \cdot T(t)$, las soluciones son:

$$u_{mn}(r, \theta, t) = J_m\!\left(\frac{z_{mn}}{a} r\right) \cos(m\theta) \cos(\omega_{mn} t)$$

- $J_m$ es la función de Bessel de primera especie y orden $m$
- $z_{mn}$ es el $n$-ésimo cero positivo de $J_m$
- $m = 0, 1, 2, \ldots$ número de **diámetros nodales**
- $n = 1, 2, 3, \ldots$ número de **círculos nodales**

**Condición de contorno:** el borde está fijo: $u(a, \theta, t) = 0$, lo que exige $J_m(z_{mn}) = 0$.

### Frecuencias propias

$$f_{mn} = \frac{z_{mn}}{2\pi a} \sqrt{\frac{T}{\rho}}$$

### Ceros de Bessel $z_{mn}$ (primeros modos)

| modo $(m,n)$ | $z_{mn}$ | frecuencia relativa a $f_{01}$ |
|:---:|:---:|:---:|
| (0,1) | 2.405 | 1.000 — fundamental |
| (1,1) | 3.832 | 1.593 |
| (2,1) | 5.136 | 2.136 |
| (0,2) | 5.520 | 2.295 |
| (3,1) | 6.380 | 2.653 |
| (1,2) | 7.016 | 2.917 |
| (4,1) | 7.588 | 3.156 |
| (2,2) | 8.417 | 3.500 |
| (0,3) | 8.654 | 3.598 |

Los sobretonos **no son armónicos** (no son múltiplos enteros del fundamental). Esto distingue a la membrana de una cuerda.

### Patrones de vibración (nodos)

```
(0,1)         (1,1)         (2,1)         (0,2)
  ·             |             X             (·)
todo sube    un diámetro   dos diámetros  un círculo
             nodal         nodales        nodal
```

---

## 2. La caja — cavidad cónica

### Geometría del atabaque

El atabaque es un **cono truncado**:
- Extremo ancho (arriba): radio $r_1$, donde va el parche
- Extremo estrecho (abajo): radio $r_2 < r_1$, abierto

La coordenada axial $x$ va de 0 (extremo estrecho) a $L$ (parche), con perfil:

$$r(x) = r_0 + x \tan\alpha$$

donde $r_0$ es el radio en $x=0$ y $\alpha$ es el semiángulo del cono.

### Ecuación de onda en un conducto de sección variable — ecuación de Webster

Para la componente axial dominante, la presión acústica $p(x,t)$ obedece:

$$\frac{\partial^2 p}{\partial x^2} + \frac{2}{r(x)}\frac{dr}{dx}\frac{\partial p}{\partial x} + k^2 p = 0$$

donde $k = \omega/c$ es el número de onda y $c \approx 343$ m/s es la velocidad del sonido en el aire.

Para un cono puro ($r(x) = x \tan\alpha$, con el vértice en $x=0$), esto se reduce a:

$$\frac{\partial^2(xp)}{\partial x^2} + k^2(xp) = 0$$

cuya solución es una onda esférica:

$$p(x) = \frac{A\, e^{ikx} + B\, e^{-ikx}}{x}$$

### Condiciones de contorno

| extremo | condición física | condición acústica |
|:---:|:---:|:---:|
| $x = L$ (parche) | el parche impone desplazamiento | presión máxima → **antinodo de presión** (aprox.) |
| $x = 0$ (abertura) | aire libre | presión ≈ 0 → **nodo de presión** |

Con estas condiciones, los modos resonantes satisfacen:

$$k_n L = n\pi, \quad n = 1, 2, 3, \ldots$$

lo que da frecuencias:

$$f_n = \frac{nc}{2L}, \quad n = 1, 2, 3, \ldots$$

**Todos los armónicos están presentes** (impares y pares), a diferencia de un cilindro cerrado-abierto donde solo aparecen los impares.

### Por qué el cono se comporta así

En el cono, la onda se expande al viajar hacia la boca ancha. El extremo estrecho —aunque sea pequeño— no puede mantener presión: cualquier exceso de presión se "escapa" por la curvatura de las ondas esféricas. Esto lo hace equivalente acústicamente a un extremo abierto, aunque geométricamente sea pequeño o casi cerrado.

### Correcciones de extremo

En la práctica, los extremos no son idealmente abiertos o cerrados. Se aplica una **corrección de longitud** $\delta$ en la abertura:

$$L_{\text{eff}} = L + \delta, \quad \delta \approx 0.6\, r_2$$

Esto desplaza ligeramente todas las frecuencias hacia abajo.

---

## 3. Acoplamiento parche–caja

El parche y la caja no son independientes: el parche fuerza al aire de la caja, y la reacción del aire modifica el movimiento del parche.

El acoplamiento es fuerte cuando una frecuencia del parche $f_{mn}$ coincide con una frecuencia de la caja $f_n$. En ese caso:

- El modo se amplifica y tiene mayor sustain
- La frecuencia resultante se desplaza ligeramente respecto a ambas frecuencias por separado (repulsión de niveles)

Cuando no coinciden, el modo se amortigua rápido.

El diseño de la caja consiste en **elegir $L$, $r_1$ y $r_2$** de forma que las resonancias de la caja coincidan con los modos del parche que quieres potenciar, normalmente el fundamental $(0,1)$ y el primer sobretono $(1,1)$.

---

## Parámetros relevantes para diseño

| parámetro | símbolo | efecto principal |
|:---:|:---:|:---|
| Radio del parche | $a$ | determina todas las frecuencias del parche ($f \propto 1/a$) |
| Tensión del parche | $T$ | sube o baja todas las frecuencias del parche ($f \propto \sqrt{T}$) |
| Densidad superficial | $\rho$ | opuesto a la tensión ($f \propto 1/\sqrt{\rho}$) |
| Longitud de la caja | $L$ | determina las resonancias de la caja ($f \propto 1/L$) |
| Ángulo del cono | $\alpha$ | modifica la forma de los modos axiales y la corrección de extremo |
| Radio base | $r_2$ | afecta la corrección de longitud $\delta$ y la radiación |

---

## 4. Medidas de referencia — Lê, Rumpi, Rum

Dimensiones interiores aproximadas de un trío estándar. Varían según el fabricante; se dan como referencia para luthería. Los diámetros de boca provienen del estándar de parches en pulgadas (Gope/Kalango); barriga y pie son valores medidos en atabaques brasileños de construcción tradicional.

| modelo | altura caja | Ø boca (arriba) | Ø barriga (máximo) | Ø pie (abajo) |
|:---:|:---:|:---:|:---:|:---:|
| **Rum**   | ~110 cm | ~28 cm (11″) | ~31 cm | ~13 cm |
| **Rumpi** | ~95 cm  | ~25 cm (10″) | ~27 cm | ~13 cm |
| **Lê**    | ~80 cm  | ~23 cm (~9″) | ~25 cm | ~12 cm |

La **barriga** se sitúa aproximadamente a 1/3 de la altura desde la boca (65 % desde el pie). La sección cónica del instrumento sigue la forma de un cono truncado con una ligera convexidad en ese punto.

El **semiángulo del cono equivalente** (boca → pie, ignorando la barriga) es:

$$\alpha = \arctan\!\left(\frac{r_\text{boca} - r_\text{pie}}{h}\right)$$

Para el Rum estándar: $\alpha \approx \arctan(7.5/110) \approx 3.9°$
