# Web principal

Stack: SvelteKit 5 (Svelte 5 runes: `$state`, `$derived`, `$effect`) + [Supabase](supabase.md) + Cloudflare Pages.

**Nombre del colectivo**: Colectivo Capoeira Libre
**URL producción**: https://colectivocapoeiralibre.es (dominio propio, comprado en Hostinger) — también sigue activo https://capoeira-colectiva.pages.dev
**Dev local**: `cd web_colectivo && npm run dev` → localhost:5173
**Deploy**: `cd web_colectivo && npm run build && wrangler pages deploy build --project-name=capoeira-colectiva --branch=main --commit-dirty=true`

Sigue las [convenciones](convenciones.md) generales del proyecto.

## Cloudflare Pages — notas de configuración

- `svelte.config.js`: `adapter-static` con `fallback: 'index.html'` (no `200.html` — Cloudflare no lo soporta como rewrite)
- `static/_redirects`: contiene `/* /index.html 200` para que SvelteKit maneje el routing client-side
- Supabase Auth: en el dashboard del proyecto → Authentication → URL Configuration, Site URL y Redirect URLs deben incluir `https://capoeira-colectiva.pages.dev/**`
- `login/+page.svelte`: el `redirectTo` del reset de contraseña apunta a `https://capoeira-colectiva.pages.dev/reset-password`

### Dominio propio (colectivocapoeiralibre.es)

Comprado por Alberto en Hostinger; el DNS se gestiona en Cloudflare (nameservers del dominio cambiados a `clara.ns.cloudflare.com` / `elmo.ns.cloudflare.com`, registro sigue en Hostinger). Añadido como Custom Domain en el proyecto Pages (Workers & Pages → capoeira-colectiva → Custom domains).

`wrangler` no tiene comando para gestionar Custom Domains de Pages — se hace desde el dashboard. Nota: el flujo de "Cloudflare Registrar" (transferir el registro del dominio a Cloudflare) no soporta `.es`, pero eso es independiente de usar Cloudflare solo como DNS + Pages, que sí funciona.

Pendiente: añadir `www.colectivocapoeiralibre.es` como Custom Domain también si se quiere que funcione con "www". Actualizar Site URL / Redirect URLs en Supabase Auth y el `redirectTo` del reset de contraseña cuando se decida cuál es el dominio canónico.

## Estructura de rutas

```
/                        ← landing pública: nombre, horarios, Instagram
/universo                ← grafo de notas (Universo Colectivo)
/universo/[slug]         ← nota individual con backlinks
/login  /registro  /reset-password

/members/                ← requiere login (auth guard en members/+layout.svelte)
    /rutinas             — gestión de rutinas; lanza el timer con ▶
    /historial           — historial agrupado por rutina
    /historial/nueva     — añadir entrada manual (sin pasar por el timer)
    /historial/[id]      — detalle de una sesión: marcas editables + borrar
    /timer               — timer con voz (solo accesible desde ▶ en rutinas)
    /descargas           — descargar app de luthería
    /mi-perfil           — nombre + cambiar contraseña + selector de voz + logout
```

**Navegación pública**: `PublicNav` con grid de 3 columnas — izquierda vacía · "Universo Colectivo" centrado · derecha vacía. En páginas `/universo/*` el link central cambia a "Home".

**Members está oculto de la navegación** (2026-09): nadie lo usaba. Se quitó el botón "Entrar/Miembros" de `PublicNav` y el icono ⬇ Descargas de `Shell.svelte`. El código y las rutas (`/login`, `/registro`, `/members/*`) siguen en el repo por si se retoma; solo dejaron de tener un enlace visible desde la web pública.

**Navegación members** (si se navega directamente a `/members/...`): Rutinas / Historial (tabbar) + ⚙ Perfil (topbar). El logo en la topbar lleva a `/`.

El `+layout.svelte` raíz ya no bloquea el render de toda la web esperando la comprobación de sesión de Supabase (`loading` store) — solo `members/+layout.svelte` sigue haciendo esa espera, porque solo esa sección necesita saber si hay usuario logueado.

## Landing pública — diseño

Hero: **sello circular SVG** con el texto `COLECTIVO · CAPOEIRA · LIBRE ·` en Cinzel siguiendo el arco del círculo, y el logo centrado dentro. Ver [paleta.md](paleta.md) para tipografía y colores.

- SVG: `viewBox="0 0 220 200"`, círculo radio 80 centrado en 110,110
- Logo: `x="52" y="42" width="120" height="120"`
- Font Cinzel cargada en `+layout.svelte` vía Google Fonts

El `main` tiene `max-width: 560px; margin: 0 auto`. El nav interior también usa ese mismo ancho para alinear bordes. Cabe sin scroll en iPhone 14 (390×844); en iPhone SE (375×667) hay scroll mínimo.

## Web pública — componentes

- `src/lib/PublicNav.svelte` — navbar con grid 3 columnas; link central cambia según ruta
- `src/lib/Graph2D.svelte` — grafo D3 force simulation para el Universo Colectivo
- `src/lib/universo.ts` — carga markdown via `import.meta.glob`, extrae títulos y `[[wiki-links]]`, construye datos del grafo, renderiza HTML
- `src/routes/paletas/+page.svelte` — herramienta interna de comparación de paletas y tipografías (no enlazada en la nav)

## Universo Colectivo

Wiki descentralizada: cada nota es un `.md` en `src/content/universo/`. Sin jerarquía — cualquier miembro puede proponer una nota. De momento solo hay `coming-soon.md`.

**Formato de nota**:
```markdown
# Título de la nota

Texto con [[slug-de-otra-nota]] como enlaces.
```

- La primera línea `# Título` es el nombre del nodo en el grafo
- Los `[[links]]` se resuelven a `/universo/slug` automáticamente
- Los backlinks (notas que apuntan a esta) aparecen al pie de la nota

**Para añadir una nota**: crear `src/content/universo/nombre-slug.md`. El grafo se actualiza al hacer build.

## Paleta de colores

Ver [paleta.md](paleta.md). Paleta cerrada: fondo crema + acento `#5e4040`.

## Modelo de datos — rutinas

```typescript
type Ex        = { name: string; duration_s: number }
type Bloque    = { name: string; exercises: Ex[] }
type BloqueLog = { name: string; exercises: Ex[]; marks: (number|null)[] }

// routines.exercises:      Bloque[]
// training_logs.exercises: BloqueLog[]
```

Ver [supabase.md](supabase.md) para el schema completo y políticas RLS.

## Convención: ejercicio "Descanso"

Un ejercicio llamado "Descanso" (insensible a mayúsculas) se trata como pausa explícita:

- **Rutinas**: no cuenta en el total de ejercicios ni aparece en los pills
- **Entrenar**: no se muestra (sin input de marca), no se guarda en el log
- **Historial**: no se muestra
- **Timer**: se trata como fase de tipo `pausa` (color teal, cuenta atrás), sin pausa automática antes

## Funcionalidades

- **Auth**: login, registro, reset-password, logout, cambio de contraseña
- **Rutinas**: crear/borrar/copiar (inmutables — no hay edición). Copiar abre el formulario de creación pre-rellenado con los datos de la original (nombre + bloques), para modificar antes de guardar. Al crear, la fecha actual se añade automáticamente al nombre (`DD/MM/YYYY`). Bloques con ejercicios. Vista colapsable con resumen (bloques · ejercicios · duración total). Copiar bloque. Botón ▶ por bloque (lanza timer con ese bloque) y ▶ en la tarjeta (lanza timer con la rutina completa).
- **Timer**: lanzado siempre desde ▶ en Rutinas — sin acceso directo desde nav.
  - **Bloque**: usa los ejercicios del bloque; config disponible: pausa, bloques (repeticiones), descanso entre bloques.
  - **Rutina completa**: encadena todos los bloques en secuencia, se ejecuta una sola vez (ROUNDS=1). Config disponible: solo pausa. Barra de puntos por bloque.
  - Durante cada ejercicio aparece un input para anotar reps. Si existe una sesión anterior para esa rutina, muestra "Última vez: X" debajo del input (cargado de `training_logs` al inicio).
  - Al terminar: botón "Guardar entreno" → guarda en `training_logs`. Sin rutina cargada: pantalla "Ve a Rutinas".
  - Voz (Web Speech API) + beeps: ejercicios cada 5s; pausas cuenta atrás 10→4; beeps en 3, 2, 1. El selector de voz está en Perfil (mi-perfil), guardado en localStorage.
- **Historial**: agrupado por rutina. Cada grupo muestra nº de sesiones y fecha más reciente, ordenado por sesión más reciente arriba. Al desplegar un grupo aparecen las sesiones (fecha + resumen); al pulsar una sesión se navega a `/historial/[id]`. Botón "+ Añadir" para registrar una sesión manualmente sin pasar por el timer.
  - `/historial/[id]`: detalle con marcas editables (guardado onblur) y botón de borrar.
  - `/historial/nueva`: elegir rutina + fecha + rellenar marcas → guarda en `training_logs`.
- **Descargas**: APK de luthería (requiere login). URL configurada en `descargas/+page.svelte` → ver [lutheria.md](lutheria.md) para el historial de releases.
- **Perfil** (`mi-perfil`): nombre, cambiar contraseña, selector de voz preferida, logout.

## Compatibilidad datos antiguos

Rutinas creadas antes de junio 2026 usaban `Ex[]` plano. `normalize()` en `rutinas/+page.svelte` las convierte a `Bloque[]` al cargar. Ver [supabase.md](supabase.md) para el SQL de limpieza.

## Pendiente

- [ ] Dominio propio

- [x] Paleta y tipografía cerradas ✓ (2026-06-06) — ver [paleta.md](paleta.md)
- [x] Diseño landing: sello circular SVG ✓ (2026-06-06)
- [x] Construir web pública ✓ (2026-06-05)
- [x] Universo Colectivo — grafo de notas ✓ (2026-06-05)
- [x] Migrar Netlify → Cloudflare Pages ✓ (2026-06-04)
