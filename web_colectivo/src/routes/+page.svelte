<script lang="ts">
	const LUTERIA_APK       = 'https://github.com/albertomanzano/capoeira-apps/releases/download/v1.0-luteria/lutheria.apk';
	const ENTRENAMIENTO_APK = 'https://github.com/albertomanzano/capoeira-apps/releases/download/v1.0-entrenamiento/entrenamiento.apk';
</script>

<svelte:head>
	<title>Colectivo Capoeira</title>
</svelte:head>

<div class="page">
	<div class="hero">
		<h1>Colectivo Capoeira</h1>
		<p>Herramientas para el entrenamiento y la luthería del berimbau.</p>
	</div>

	<div class="cards">
		<div class="card">
			<div class="card-icon">🥋</div>
			<div class="card-body">
				<h2>Entrenamiento</h2>
				<p>Timer para clases, registro de marcas por ejercicio e historial de progreso individual.</p>
				<div class="meta">Android · v1.0</div>
			</div>
			<a href={ENTRENAMIENTO_APK} class="btn-download">Descargar APK</a>
		</div>

		<div class="card">
			<div class="card-icon">🪘</div>
			<div class="card-body">
				<h2>Luthería</h2>
				<p>Mide y casa cabaças con biribas. Calcula la frecuencia de Helmholtz y encuentra la biriba compatible.</p>
				<div class="meta">Android · v1.0</div>
			</div>
			<a href={LUTERIA_APK} class="btn-download btn-secondary">Descargar APK</a>
		</div>
	</div>
</div>

<style>
	.page {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 56px 20px 48px;
	}

	.hero {
		text-align: center;
		margin-bottom: 48px;
	}
	.hero h1 {
		font-size: 2rem;
		font-weight: 800;
		color: #4ade80;
		margin-bottom: 10px;
	}
	.hero p {
		color: #555;
		font-size: 1rem;
		max-width: 320px;
		margin: 0 auto;
	}

	.cards {
		display: flex;
		flex-direction: column;
		gap: 16px;
		width: 100%;
		max-width: 420px;
	}

	.card {
		background: #1a1a1a;
		border-radius: 16px;
		padding: 24px;
		display: flex;
		flex-direction: column;
		gap: 16px;
		border: 1px solid #222;
	}

	.card-icon { font-size: 2rem; }

	.card-body h2 {
		font-size: 1.25rem;
		font-weight: 700;
		margin-bottom: 8px;
	}
	.card-body p {
		font-size: 0.88rem;
		color: #888;
		line-height: 1.5;
		margin-bottom: 8px;
	}
	.meta {
		font-size: 0.72rem;
		color: #444;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.btn-download {
		display: block;
		text-align: center;
		padding: 14px;
		background: #4ade80;
		color: #0f0f0f;
		font-weight: 700;
		font-size: 1rem;
		border-radius: 12px;
		text-decoration: none;
	}
	.btn-download:hover { background: #86efac; }
	.btn-download.btn-secondary {
		background: #1e1e1e;
		color: #888;
		border: 1px solid #2a2a2a;
	}
	.btn-download.btn-secondary:hover { background: #252525; }
</style>
