<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import Shell from '$lib/Shell.svelte';

	let name        = $state('');
	let newPassword = $state('');
	let pwBusy      = $state(false);
	let pwError     = $state('');
	let pwSuccess   = $state(false);

	async function load() {
		const { data: { user } } = await supabase.auth.getUser();
		if (!user) return;
		const { data: profile } = await supabase
			.from('profiles')
			.select('name')
			.eq('id', user.id)
			.single();
		name = profile?.name ?? '';
	}

	async function changePassword() {
		if (newPassword.length < 6) { pwError = 'Mínimo 6 caracteres'; return; }
		pwBusy = true; pwError = ''; pwSuccess = false;
		const { error } = await supabase.auth.updateUser({ password: newPassword });
		if (error) { pwError = error.message; pwBusy = false; return; }
		pwSuccess = true; newPassword = ''; pwBusy = false;
	}

	$effect(() => { load(); });
</script>

<Shell tab="perfil">
	<p class="section-label">Cuenta</p>
	<div class="name-card">
		<span class="name">{name || '…'}</span>
	</div>

	<p class="section-label" style="margin-top:24px">Cambiar contraseña</p>
	<div class="pw-row">
		<input type="password" bind:value={newPassword} placeholder="Nueva contraseña" minlength="6" />
		<button class="pw-btn" onclick={changePassword} disabled={pwBusy}>
			{pwBusy ? '…' : 'Cambiar'}
		</button>
	</div>
	{#if pwError}<p class="pw-error">{pwError}</p>{/if}
	{#if pwSuccess}<p class="pw-ok">Contraseña actualizada</p>{/if}

	<div class="sep"></div>
	<button class="btn-secondary" onclick={() => goto('/rutinas')}>Mis rutinas</button>
</Shell>

<style>
	.section-label {
		font-size: 0.72rem; color: #444; text-transform: uppercase;
		letter-spacing: 1px; margin-bottom: 10px;
	}
	.name-card {
		background: #1a1a1a; border-radius: 10px;
		padding: 14px 16px; margin-bottom: 8px;
	}
	.name { font-size: 1rem; font-weight: 600; }
	.pw-row { display: flex; gap: 8px; margin-bottom: 8px; }
	.pw-row input { flex: 1; }
	.pw-btn {
		padding: 0 16px; background: #1a1a1a; border: 1px solid #2a2a2a;
		color: #888; border-radius: 8px; cursor: pointer; font-size: 0.9rem; white-space: nowrap;
	}
	.pw-error { color: #ef4444; font-size: 0.8rem; margin-top: 4px; }
	.pw-ok    { color: #4ade80; font-size: 0.8rem; margin-top: 4px; }
	.sep { height: 1px; background: #1a1a1a; margin: 24px 0; }
</style>
