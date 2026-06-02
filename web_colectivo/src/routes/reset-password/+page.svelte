<script lang="ts">
	import { onMount } from 'svelte';
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';

	let newPassword = $state('');
	let busy    = $state(false);
	let error   = $state('');
	let ready   = $state(false);

	onMount(async () => {
		// Token may have been processed before component mounted
		const { data: { session } } = await supabase.auth.getSession();
		if (session) { ready = true; return; }

		const { data } = supabase.auth.onAuthStateChange((event) => {
			if (event === 'PASSWORD_RECOVERY' || event === 'SIGNED_IN') ready = true;
		});
		return () => data.subscription.unsubscribe();
	});

	async function update() {
		if (newPassword.length < 6) { error = 'Mínimo 6 caracteres'; return; }
		busy = true; error = '';
		const { error: err } = await supabase.auth.updateUser({ password: newPassword });
		if (err) { error = err.message; busy = false; return; }
		goto('/mi-perfil');
	}
</script>

<div class="wrap">
	<h1>Capoeira</h1>
	{#if ready}
		<p class="subtitle">Nueva contraseña</p>
		<form onsubmit={(e) => { e.preventDefault(); update(); }}>
			<div class="field">
				<label>Nueva contraseña</label>
				<input type="password" bind:value={newPassword} placeholder="••••••••" minlength="6" required />
			</div>
			{#if error}<p class="error">{error}</p>{/if}
			<button class="btn-primary" type="submit" disabled={busy}>
				{busy ? 'Guardando…' : 'Guardar contraseña'}
			</button>
		</form>
	{:else}
		<p class="subtitle">Verificando enlace…</p>
	{/if}
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
</style>
