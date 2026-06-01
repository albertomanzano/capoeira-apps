<script lang="ts">
	const LUTERIA_APK = 'https://github.com/albertomanzano/capoeira-apps/releases/download/v1.0-luteria/lutheria.apk';
</script>

<svelte:head>
	<title>Apps — Colectivo Capoeira</title>
</svelte:head>

<div class="page">
	<div class="hero">
		<h1>Apps del Colectivo</h1>
		<p>Herramientas para el entrenamiento y la luthería del berimbau.</p>
	</div>

	<div class="cards">
		<div class="card">
			<div class="card-icon">🪘</div>
			<div class="card-body">
				<h2>Luthería</h2>
				<p>Mide y casa cabaças con biribas. Calcula la frecuencia de Helmholtz y encuentra la biriba compatible.</p>
				<div class="meta">Android · Python/Flet · v1.0</div>
			</div>
			<a href={LUTERIA_APK} class="btn-download" download>
				Descargar APK
			</a>
		</div>

		<div class="card card--soon">
			<div class="card-icon">🥋</div>
			<div class="card-body">
				<h2>Entrenamiento</h2>
				<p>Timer para clases, registro de marcas por ejercicio e historial de progreso individual.</p>
				<div class="meta">Android · En desarrollo</div>
			</div>
			<span class="btn-soon">Próximamente</span>
		</div>
	</div>

	<div class="footer-note">
		¿Eres alumno del Colectivo? <a href="/login">Accede a tu perfil →</a>
	</div>
</div>

<style>
	.page {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 48px 20px 40px;
		background: #0f0f0f;
	}

	.hero {
		text-align: center;
		margin-bottom: 40px;
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
	.card--soon {
		opacity: 0.6;
	}

	.card-icon {
		font-size: 2rem;
	}
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

	.btn-soon {
		display: block;
		text-align: center;
		padding: 14px;
		background: #1e1e1e;
		color: #444;
		font-weight: 700;
		font-size: 1rem;
		border-radius: 12px;
		border: 1px solid #2a2a2a;
	}

	.footer-note {
		margin-top: 40px;
		font-size: 0.85rem;
		color: #444;
		text-align: center;
	}
	.footer-note a {
		color: #4ade80;
		text-decoration: none;
	}
</style>
