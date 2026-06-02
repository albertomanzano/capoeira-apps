<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';

	let name     = $state('');
	let email    = $state('');
	let password = $state('');
	let error    = $state('');
	let busy     = $state(false);

	async function register() {
		if (!name.trim()) { error = 'Escribe tu nombre'; return; }
		busy = true; error = '';
		const { data, error: err } = await supabase.auth.signUp({ email, password });
		if (err) { error = err.message; busy = false; return; }
		if (data.user) {
			const { error: profileErr } = await supabase
				.from('profiles')
				.insert({ id: data.user.id, name: name.trim(), role: 'alumno' });
			if (profileErr) { error = profileErr.message; busy = false; return; }
		}
		goto('/mi-perfil');
	}
</script>

<div class="wrap">
	<h1>Capoeira</h1>
	<p class="subtitle">Crear cuenta</p>

	<form onsubmit={(e) => { e.preventDefault(); register(); }}>
		<div class="field">
			<label>Nombre</label>
			<input type="text" bind:value={name} placeholder="Tu nombre" required />
		</div>
		<div class="field">
			<label>Email</label>
			<input type="email" bind:value={email} placeholder="tu@email.com" required />
		</div>
		<div class="field">
			<label>Contraseña</label>
			<input type="password" bind:value={password} placeholder="••••••••" minlength="6" required />
		</div>

		{#if error}<p class="error">{error}</p>{/if}

		<button class="btn-primary" type="submit" disabled={busy}>
			{busy ? 'Creando cuenta…' : 'Crear cuenta'}
		</button>
	</form>
	<p class="login-link">¿Ya tienes cuenta? <a href="/login">Entrar</a></p>
</div>

<style>
	.wrap {
		max-width: 360px; margin: 0 auto;
		padding: 80px 24px 24px;
		display: flex; flex-direction: column; gap: 24px;
	}
	h1 { font-size: 2rem; font-weight: 800; text-align: center; color: #4ade80; }
	.subtitle { text-align: center; color: #555; font-size: 0.9rem; margin-top: -16px; }
	form { display: flex; flex-direction: column; gap: 16px; }
	.field { display: flex; flex-direction: column; gap: 6px; }
	label { font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 1px; }
	.error { color: #ef4444; font-size: 0.85rem; text-align: center; }
	.login-link { text-align: center; font-size: 0.85rem; color: #444; }
	.login-link a { color: #4ade80; text-decoration: none; }
</style>
