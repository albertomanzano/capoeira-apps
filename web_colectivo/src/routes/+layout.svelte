<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { user, role, loading } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { children } = $props();

	$effect(() => {
		if ($loading) return;
		const path = $page.url.pathname;
		const publicPaths = ['/login', '/registro', '/reset-password'];
		if (!$user && !publicPaths.includes(path)) { goto('/login'); return; }
		if ($user && $role !== 'profe' && (path === '/alumnos' || path.startsWith('/alumnos/'))) {
			goto('/rutinas');
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<style>
	:global(*) { box-sizing: border-box; margin: 0; padding: 0; }
	:global(body) {
		font-family: system-ui, sans-serif;
		background: #0f0f0f;
		color: #fff;
		min-height: 100vh;
	}
	:global(input), :global(select) {
		width: 100%;
		background: #1a1a1a;
		border: 1px solid #2a2a2a;
		color: #fff;
		border-radius: 8px;
		padding: 12px;
		font-size: 1rem;
	}
	:global(input:focus), :global(select:focus) { outline: none; border-color: #4ade80; }
	:global(.btn-primary) {
		display: block; width: 100%;
		padding: 16px; background: #4ade80; color: #0f0f0f;
		border: none; border-radius: 12px;
		font-size: 1.05rem; font-weight: 700; cursor: pointer; margin-bottom: 10px;
	}
	:global(.btn-primary:disabled) { background: #1e3a2a; color: #2d5a3d; cursor: default; }
	:global(.btn-secondary) {
		display: block; width: 100%;
		padding: 14px; background: #1a1a1a; color: #888;
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
