<script lang="ts">
	import logo from '$lib/assets/logo.svg';
	let { tab, children } = $props<{ tab: string; children: any }>();
</script>

<div class="shell">
	<div class="topbar">
		<a href="/"><img src={logo} alt="Capoeira Colectiva" class="logo" /></a>
		<div class="topbar-right">
			<a href="/members/mi-perfil" class="top-link" class:active={tab === 'perfil'} title="Ajustes">⚙</a>
		</div>
	</div>

	<div class="content">
		{@render children()}
	</div>

	<nav class="tabbar">
		<a href="/members/rutinas"  class:active={tab === 'rutinas'}>
			<span class="icon">📋</span><span>Rutinas</span>
		</a>
		<a href="/members/historial" class:active={tab === 'historial'}>
			<span class="icon">📊</span><span>Historial</span>
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
		padding: 8px 16px;
		border-bottom: 1px solid var(--border);
	}
	.logo { height: 100px; width: auto; }
	.topbar-right { display: flex; align-items: center; gap: 14px; }
	.top-link {
		color: #444; font-size: 1.6rem; text-decoration: none;
		transition: color 0.15s; line-height: 1; padding: 4px;
	}
	.top-link.active { color: var(--accent); }
	.top-link:hover  { color: #888; }
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
		background: var(--bg);
		border-top: 1px solid var(--border);
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
	.tabbar a.active { color: var(--accent); }
	.icon { font-size: 1.3rem; line-height: 1; }
</style>
