<script lang="ts">
	import Shell from '$lib/Shell.svelte';
	const LUTERIA_APK = 'https://github.com/albertomanzano/capoeira-apps/releases/download/v1.0-luteria/lutheria.apk';
</script>

<svelte:head>
	<title>Apps — Colectivo Capoeira</title>
</svelte:head>

<Shell tab="descargas">
	<h1 class="title">Descargas</h1>
	<div class="cards">
		<div class="card">
			<div class="card-icon">🪘</div>
			<div class="card-body">
				<h2>App de luthería</h2>
				<p>Mide y casa cabaças con biribas. Calcula la frecuencia de Helmholtz y encuentra la biriba compatible.</p>
				<div class="meta">Android · Python/Flet · v1.0</div>
			</div>
			<a href={LUTERIA_APK} class="btn-download" download>
				Descargar APK
			</a>
		</div>
	</div>
</Shell>

<style>
	.title { font-size: 1.4rem; font-weight: 700; margin-bottom: 16px; }

	.cards { display: flex; flex-direction: column; gap: 16px; }

	.card {
		background: var(--surface);
		border-radius: 16px;
		padding: 24px;
		display: flex;
		flex-direction: column;
		gap: 16px;
		border: 1px solid var(--border);
	}
	.card-icon { font-size: 2rem; }
	.card-body h2 { font-size: 1.1rem; font-weight: 700; margin-bottom: 6px; }
	.card-body p { font-size: 0.88rem; color: #888; line-height: 1.5; margin-bottom: 6px; }
	.meta { font-size: 0.72rem; color: #444; text-transform: uppercase; letter-spacing: 0.5px; }

	.btn-download {
		display: block; text-align: center;
		padding: 14px; background: var(--accent); color: var(--accent-on);
		font-weight: 700; font-size: 1rem; border-radius: 12px; text-decoration: none;
	}
	.btn-download:hover { background: #86efac; }
</style>
