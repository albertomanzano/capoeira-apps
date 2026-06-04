<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { loading } from '$lib/stores/auth';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<style>
	:global(:root) {
		--accent:        #5c3318;
		--accent-on:     #f5ede0;
		--text:          #2e1c0e;
		--bg:            #f5ede0;
		--surface:       #ece4d3;
		--surface-hover: #e3daca;
		--border:        #cec0af;
	}
	:global(*) { box-sizing: border-box; margin: 0; padding: 0; }
	:global(body) {
		font-family: system-ui, sans-serif;
		background: var(--bg);
		color: var(--text);
		min-height: 100vh;
	}
	:global(input), :global(select) {
		width: 100%;
		background: var(--surface);
		border: 1px solid var(--border);
		color: var(--text);
		border-radius: 8px;
		padding: 12px;
		font-size: 1rem;
	}
	:global(input:focus), :global(select:focus) { outline: none; border-color: var(--accent); }
	:global(.btn-primary) {
		display: block; width: 100%;
		padding: 16px; background: var(--accent); color: var(--accent-on);
		border: none; border-radius: 12px;
		font-size: 1.05rem; font-weight: 700; cursor: pointer; margin-bottom: 10px;
	}
	:global(.btn-primary:disabled) { opacity: 0.35; cursor: default; }
	:global(.btn-secondary) {
		display: block; width: 100%;
		padding: 14px; background: var(--surface); color: #888;
		border: none; border-radius: 12px;
		font-size: 0.95rem; font-weight: 600; cursor: pointer; margin-bottom: 10px;
	}
</style>

{#if $loading}
	<div style="display:flex;align-items:center;justify-content:center;height:100vh;color:#333">
		Cargando…
	</div>
{:else}
	{@render children()}
{/if}
