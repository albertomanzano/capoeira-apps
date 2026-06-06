<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com"/>
	<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Raleway:wght@500;700&family=Josefin+Sans:wght@400;700&family=Jost:wght@400;700&family=Montserrat:wght@400;700&family=Nunito:wght@400;700&family=DM+Sans:wght@400;700&display=swap" rel="stylesheet"/>
</svelte:head>

<script lang="ts">
	import logo from '$lib/assets/logo.svg';

	const fuentes = [
		{ nombre: 'System UI (actual)', font: 'system-ui' },
		{ nombre: 'Raleway',            font: "'Raleway', sans-serif" },
		{ nombre: 'Josefin Sans',       font: "'Josefin Sans', sans-serif" },
		{ nombre: 'Jost',               font: "'Jost', sans-serif" },
		{ nombre: 'Montserrat',         font: "'Montserrat', sans-serif" },
		{ nombre: 'DM Sans',            font: "'DM Sans', sans-serif" },
		{ nombre: 'Nunito',             font: "'Nunito', sans-serif" },
	];

	const bg = '#f5ede0', surface = '#ece4d3', border = '#cec0af', text = '#2e1c0e', accent = '#5e4040', accentOn = '#f5ede0';
</script>

<div class="page">
	<div class="grid">
		{#each fuentes as f}
			<div class="mockup" style="--mfont:{f.font}; background:{bg}; border-color:{border}; color:{text}">

				<!-- nav -->
				<div class="m-nav" style="border-color:{border}">
					<span class="m-nav-link">Universo Colectivo</span>
					<span class="m-btn" style="background:{accent}; color:{accentOn}">Entrar</span>
				</div>

				<!-- hero sello -->
				<div class="m-hero">
					<svg viewBox="0 0 220 200" class="m-sello">
						<defs>
							<path id="cp-{f.nombre.replace(/\s/g,'')}" d="M 110,110 m -80,0 a 80,80 0 1,1 160,0 a 80,80 0 1,1 -160,0"/>
						</defs>
						<text font-family="'Cinzel', serif" font-size="13" font-weight="700" fill={accent} letter-spacing="3">
							<textPath href="#cp-{f.nombre.replace(/\s/g,'')}" startOffset="0%">COLECTIVO · CAPOEIRA · LIBRE ·</textPath>
						</text>
						<image href={logo} x="52" y="42" width="120" height="120"/>
					</svg>
				</div>

				<!-- cards horarios -->
				<div class="m-cards">
					<div class="m-card" style="background:{surface}; border-color:{border}">
						<p class="m-card-day" style="color:{accent}">Lunes y martes</p>
						<p class="m-card-place" style="color:{text}">Ermita de la Virgen del Puerto</p>
						<p class="m-card-time" style="color:{text}">20:30 – 22:00</p>
					</div>
					<div class="m-card" style="background:{surface}; border-color:{border}">
						<p class="m-card-day" style="color:{accent}">Jueves</p>
						<p class="m-card-place" style="color:{text}">SOMA SHC</p>
						<p class="m-card-time" style="color:{text}">20:00 – 22:00</p>
					</div>
				</div>

				<!-- instagram -->
				<div class="m-social">
					<span class="m-ig" style="color:{accent}; border-color:{accent}">@colectivocapoeiralibre.madrid</span>
				</div>

				<p class="m-label">{f.nombre}</p>
			</div>
		{/each}
	</div>
</div>

<style>
	:global(body) { margin: 0; }
	.page {
		padding: 32px 24px 48px;
		background: #d0cdc8;
		min-height: 100vh;
		font-family: system-ui, sans-serif;
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
		gap: 20px;
	}

	.mockup {
		border: 1px solid;
		border-radius: 16px;
		overflow: hidden;
		font-family: var(--mfont);
		display: flex;
		flex-direction: column;
	}

	/* nav */
	.m-nav {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 12px;
		padding: 10px 14px;
		border-bottom: 1px solid;
	}
	.m-nav-link { font-size: 0.72rem; opacity: 0.65; }
	.m-btn {
		font-size: 0.7rem;
		font-weight: 700;
		padding: 5px 12px;
		border-radius: 6px;
	}

	/* hero */
	.m-hero { display: flex; justify-content: center; padding: 8px 0 4px; }
	.m-sello { width: 160px; height: 146px; }

	/* cards */
	.m-cards { display: flex; flex-direction: column; gap: 6px; padding: 8px 14px; }
	.m-card { border: 1px solid; border-radius: 8px; padding: 10px 12px; }
	.m-card-day { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 3px; }
	.m-card-place { font-size: 0.78rem; font-weight: 600; }
	.m-card-time { font-size: 0.72rem; opacity: 0.6; }

	/* social */
	.m-social { display: flex; justify-content: center; padding: 10px 14px 12px; }
	.m-ig { font-size: 0.65rem; font-weight: 700; border: 1.5px solid; padding: 6px 12px; border-radius: 8px; }

	.m-label {
		text-align: center;
		font-size: 0.6rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.8px;
		color: #888;
		padding: 6px 0 10px;
		font-family: system-ui;
	}
</style>
