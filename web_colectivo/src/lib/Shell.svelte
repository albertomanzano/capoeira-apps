<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import { role } from '$lib/stores/auth';

	let { tab, children } = $props<{ tab: string; children: any }>();

	async function logout() {
		await supabase.auth.signOut();
		goto('/login');
	}
</script>

<div class="shell">
	<div class="topbar">
		<span class="brand">Capoeira</span>
		<div class="topbar-right">
			{#if $role === 'profe'}
				<a href="/alumnos" class="top-link" class:active={tab === 'alumnos'}>Alumnos</a>
			{/if}
			<a href="/mi-perfil" class="top-link" class:active={tab === 'perfil'} title="Perfil">⚙</a>
			<button class="logout" onclick={logout}>Salir</button>
		</div>
	</div>

	<div class="content">
		{@render children()}
	</div>

	<nav class="tabbar">
		<a href="/rutinas"  class:active={tab === 'rutinas'}>
			<span class="icon">📋</span><span>Rutinas</span>
		</a>
		<a href="/entrenar" class:active={tab === 'entrenar'}>
			<span class="icon">💪</span><span>Entrenar</span>
		</a>
		<a href="/historial" class:active={tab === 'historial'}>
			<span class="icon">📊</span><span>Historial</span>
		</a>
		<a href="/timer" class:active={tab === 'timer'}>
			<span class="icon">⏱</span><span>Timer</span>
		</a>
	</nav>
</div>

<style>
	.shell {
		max-width: 480px;
		margin: 0 auto;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}
	.topbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 14px 16px;
		border-bottom: 1px solid #1a1a1a;
	}
	.brand { font-weight: 700; font-size: 1rem; color: #4ade80; letter-spacing: 1px; text-transform: uppercase; }
	.topbar-right { display: flex; align-items: center; gap: 14px; }
	.top-link {
		color: #444; font-size: 0.85rem; text-decoration: none;
		transition: color 0.15s;
	}
	.top-link.active { color: #4ade80; }
	.top-link:hover  { color: #888; }
	.logout { background: none; border: none; color: #444; cursor: pointer; font-size: 0.85rem; }
	.logout:hover { color: #888; }
	.content {
		flex: 1;
		padding: 16px;
		padding-bottom: 90px;
		overflow-y: auto;
	}
	.tabbar {
		position: fixed;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 100%;
		max-width: 480px;
		display: flex;
		background: #0a0a0a;
		border-top: 1px solid #1e1e1e;
		z-index: 100;
		padding-bottom: env(safe-area-inset-bottom, 0px);
	}
	.tabbar a {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 3px;
		padding: 10px 0 13px;
		text-decoration: none;
		color: #444;
		font-size: 0.68rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		transition: color 0.15s;
	}
	.tabbar a.active { color: #4ade80; }
	.icon { font-size: 1.3rem; line-height: 1; }
</style>
