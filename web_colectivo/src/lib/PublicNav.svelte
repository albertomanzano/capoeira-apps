<script lang="ts">
	import { page } from '$app/stores';
	import { user } from '$lib/stores/auth';

	const inUniverso = $derived($page.url.pathname.startsWith('/universo'));
</script>

<nav>
	<div class="inner">
		<div class="left"></div>
		{#if inUniverso}
			<a href="/" class="center">Home</a>
		{:else}
			<a href="/universo" class="center">Universo Colectivo</a>
		{/if}
		<div class="right">
			{#if $user}
				<a href="/members/rutinas" class="btn-entrar">Miembros</a>
			{:else}
				<a href="/login" class="btn-entrar">Entrar</a>
			{/if}
		</div>
	</div>
</nav>

<style>
	nav {
		border-bottom: 1px solid var(--border);
		background: var(--bg);
		position: sticky;
		top: 0;
		z-index: 10;
	}
	.inner {
		max-width: 560px;
		margin: 0 auto;
		padding: 14px 20px;
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: center;
	}
	.left { }
	.center {
		text-decoration: none;
		color: var(--text);
		font-size: 0.9rem;
		opacity: 0.65;
		transition: opacity 0.15s;
		white-space: nowrap;
		text-align: center;
	}
	.center:hover { opacity: 1; }
	.right {
		display: flex;
		justify-content: flex-end;
	}
	.btn-entrar {
		text-decoration: none;
		background: var(--accent);
		color: var(--accent-on);
		padding: 7px 16px;
		border-radius: 8px;
		font-weight: 600;
		font-size: 0.9rem;
		transition: opacity 0.15s;
	}
	.btn-entrar:hover { opacity: 0.85; }
</style>
