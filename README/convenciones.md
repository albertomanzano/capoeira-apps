# Convenciones del proyecto

Aplican tanto a la [web](web.md) como a la [app de luthería](lutheria.md).

## Generales

- Notas musicales en solfeo (Do, Re, Mi, Fa, Sol, La, Si) — nunca notación anglosajona
- Sin comentarios en el código salvo que el motivo no sea obvio
- Documentos de física en Markdown con LaTeX

## Python / Flet

- Virtualenv compartido: `atabaque_venv/` en la raíz del proyecto
- Activar: `source atabaque_venv/bin/activate`

## SvelteKit / TypeScript

- Svelte 5 runes: `$state`, `$derived`, `$effect`
- Inputs anidados en `{#each}`: usar `oninput` con índice explícito, no `bind:value` (poco fiable con proxies reactivos en Svelte 5)
- Colores en CSS: siempre hex 6 dígitos

## Git

- Claude hace commit y push tras cada sesión — Alberto no gestiona git directamente
- Repo: `https://github.com/albertomanzano/capoeira-apps.git`
- Push requiere credenciales de Alberto (Claude no las tiene almacenadas)

## Workflow de desarrollo

- Probar siempre en local (`npm run dev`) antes de hacer deploy
- Deploy a Cloudflare Pages solo al final de la sesión, cuando Alberto confirma que funciona
- Ver [web.md](web.md) para el comando de deploy exacto

## Knowledge management

- CLAUDE.md es el índice — apunta a README/ con contexto suficiente para navegar
- README/ contiene docs atómicos — cada uno con ≥1 inlink, ≥1 outlink, ≥3 links totales
- Claude actualiza CLAUDE.md y README/ durante la sesión, no al final
- Memory solo para perfil de Alberto y feedback sobre el comportamiento de Claude — nunca para estado técnico
