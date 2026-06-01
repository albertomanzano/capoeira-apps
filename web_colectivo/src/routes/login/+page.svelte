<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import { user, role } from '$lib/stores/auth';

	let email    = $state('');
	let password = $state('');
	let error    = $state('');
	let info     = $state('');
	let busy     = $state(false);
	let forgotMode = $state(false);

	$effect(() => {
		if ($user && $role !== null) goto($role === 'alumno' ? '/mi-perfil' : '/sesiones');
	});

	async function login() {
		busy = true; error = '';
		const { error: err } = await supabase.auth.signInWithPassword({ email, password });
		if (err) error = err.message;
		busy = false;
	}

	async function sendReset() {
		if (!email.trim()) { error = 'Escribe tu email'; return; }
		busy = true; error = ''; info = '';
		const { error: err } = await supabase.auth.resetPasswordForEmail(email, {
			redirectTo: 'https://capoeiracolectiva.netlify.app/reset-password',
		});
		if (err) error = err.message;
		else info = 'Email enviado. Revisa tu bandeja.';
		busy = false;
	}
</script>

<div class="wrap">
	<h1>Capoeira</h1>

	{#if !forgotMode}
		<form onsubmit={(e) => { e.preventDefault(); login(); }}>
			<div class="field">
				<label>Email</label>
				<input type="email" bind:value={email} placeholder="tu@email.com" required />
			</div>
			<div class="field">
				<label>Contraseña</label>
				<input type="password" bind:value={password} placeholder="••••••••" required />
			</div>
			{#if error}<p class="error">{error}</p>{/if}
			<button class="btn-primary" type="submit" disabled={busy}>
				{busy ? 'Entrando…' : 'Entrar'}
			</button>
		</form>
		<p class="register-link">¿Primera vez? <a href="/registro">Crear cuenta</a></p>
		<p class="register-link"><button class="link-btn" onclick={() => forgotMode = true}>Olvidé mi contraseña</button></p>
	{:else}
		<form onsubmit={(e) => { e.preventDefault(); sendReset(); }}>
			<div class="field">
				<label>Tu email</label>
				<input type="email" bind:value={email} placeholder="tu@email.com" required />
			</div>
			{#if error}<p class="error">{error}</p>{/if}
			{#if info}<p class="info">{info}</p>{/if}
			<button class="btn-primary" type="submit" disabled={busy}>
				{busy ? 'Enviando…' : 'Enviar enlace'}
			</button>
		</form>
		<p class="register-link"><button class="link-btn" onclick={() => forgotMode = false}>Volver</button></p>
	{/if}
</div>

<style>
	.wrap {
		max-width: 360px;
		margin: 0 auto;
		padding: 80px 24px 24px;
		display: flex;
		flex-direction: column;
		gap: 32px;
	}
	h1 {
		font-size: 2rem;
		font-weight: 800;
		text-align: center;
		color: #4ade80;
	}
	form { display: flex; flex-direction: column; gap: 16px; }
	.field { display: flex; flex-direction: column; gap: 6px; }
	label { font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 1px; }
	.error { color: #ef4444; font-size: 0.85rem; text-align: center; }
	.register-link { text-align: center; font-size: 0.85rem; color: #444; }
	.register-link a { color: #4ade80; text-decoration: none; }
	.link-btn { background: none; border: none; color: #4ade80; cursor: pointer; font-size: 0.85rem; padding: 0; }
	.info { color: #4ade80; font-size: 0.85rem; text-align: center; }
</style>
