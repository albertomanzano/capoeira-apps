<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com"/>
	<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap" rel="stylesheet"/>
</svelte:head>

<script lang="ts">
	import PublicNav from '$lib/PublicNav.svelte';
	import logo from '$lib/assets/logo.svg';
</script>

<PublicNav />

<main>
	<section class="hero">
		<svg viewBox="0 0 220 200" class="sello">
			<defs>
				<path id="circleHero" d="M 110,110 m -80,0 a 80,80 0 1,1 160,0 a 80,80 0 1,1 -160,0"/>
			</defs>
			<text font-family="'Cinzel', serif" font-size="13" font-weight="700" fill="var(--accent)" letter-spacing="3">
				<textPath href="#circleHero" startOffset="0%">COLECTIVO · CAPOEIRA · LIBRE ·</textPath>
			</text>
			<image href={logo} x="52" y="42" width="120" height="120"/>
		</svg>
	</section>

	<section class="info">
		<div class="card">
			<div>
				<h2>Lunes y jueves</h2>
				<a href="https://maps.app.goo.gl/bRTa2HJnmhZTVYX16" target="_blank" rel="noopener noreferrer" class="place">El Girasol</a>
				<p class="detail">20:00 – 22:00</p>
			</div>
		</div>
	</section>

	<section class="social">
		<a
			href="https://www.instagram.com/colectivocapoeiralibre.madrid/"
			target="_blank"
			rel="noopener noreferrer"
			class="ig-link"
		>
			<svg viewBox="0 0 24 24" fill="currentColor" class="ig-icon">
				<path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
			</svg>
			@colectivocapoeiralibre.madrid
		</a>
	</section>
</main>

<style>
	main {
		max-width: 560px;
		margin: 0 auto;
		padding: 0 20px 48px;
	}

	.hero {
		padding: 12px 0 4px;
		border-bottom: 1px solid var(--border);
		display: flex;
		justify-content: center;
	}
	.sello { width: 320px; height: 320px; }

.info {
		display: flex;
		flex-direction: column;
		gap: 12px;
		padding: 32px 0;
		border-bottom: 1px solid var(--border);
	}
	.card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 20px;
	}
	h2 {
		font-size: 0.7rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 1px;
		color: var(--accent);
		margin-bottom: 8px;
	}
	.place {
		display: block;
		font-size: 1rem;
		font-weight: 600;
		color: var(--accent);
		text-decoration: none;
		line-height: 1.4;
		margin-bottom: 4px;
	}
	.place:hover { text-decoration: underline; }
	.card .detail {
		font-weight: 400;
		font-size: 0.9rem;
		opacity: 0.65;
	}

	.schedule { display: flex; flex-direction: column; gap: 6px; }
	.schedule-row {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 12px;
	}
	.day { font-size: 1rem; font-weight: 600; color: var(--text); }
	.time { font-size: 0.95rem; color: var(--text); opacity: 0.65; white-space: nowrap; }

	.social {
		padding-top: 32px;
		display: flex;
		justify-content: center;
	}
	.ig-link {
		display: flex;
		align-items: center;
		gap: 10px;
		text-decoration: none;
		color: var(--accent);
		font-weight: 700;
		font-size: 1rem;
		border: 2px solid var(--accent);
		padding: 12px 24px;
		border-radius: 12px;
		transition: background 0.15s, color 0.15s;
	}
	.ig-link:hover {
		background: var(--accent);
		color: var(--accent-on);
	}
	.ig-icon {
		width: 20px;
		height: 20px;
		flex-shrink: 0;
	}
</style>
