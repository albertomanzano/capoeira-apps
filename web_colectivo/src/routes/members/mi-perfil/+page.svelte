<script lang="ts">
	import { onMount } from 'svelte';
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import Shell from '$lib/Shell.svelte';

	let name        = $state('');
	let newPassword = $state('');
	let pwBusy      = $state(false);
	let pwError     = $state('');
	let pwSuccess   = $state(false);

	let voices        = $state<SpeechSynthesisVoice[]>([]);
	let selectedVoice = $state<SpeechSynthesisVoice | null>(null);

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

	async function logout() {
		await supabase.auth.signOut();
		goto('/login');
	}

	function populateVoices() {
		const v = window.speechSynthesis.getVoices();
		if (!v.length) return;
		voices = v;
		const saved = localStorage.getItem('capoeira_voice');
		const match = saved ? v.find(x => x.name === saved) : null;
		if (match) { selectedVoice = match; return; }
		const spanish = v.filter(x => x.lang.startsWith('es'));
		const premium = spanish.find(x => /natural|neural|premium|enhanced/i.test(x.name));
		selectedVoice = premium || spanish[0] || v[0] || null;
	}

	function selectVoice(i: number) {
		selectedVoice = voices[i];
		if (selectedVoice) localStorage.setItem('capoeira_voice', selectedVoice.name);
	}

	function testVoice() {
		if (!window.speechSynthesis) return;
		window.speechSynthesis.cancel();
		const utt = new SpeechSynthesisUtterance('Ejercicio uno. Diez. Veinte. Treinta.');
		utt.lang = 'es-ES'; utt.rate = 0.88; utt.pitch = 1.0;
		if (selectedVoice) utt.voice = selectedVoice;
		window.speechSynthesis.speak(utt);
	}

	onMount(() => {
		load();
		if (typeof window !== 'undefined' && window.speechSynthesis) {
			window.speechSynthesis.onvoiceschanged = populateVoices;
			populateVoices();
		}
	});
</script>

<Shell tab="perfil">
	<div class="header"><h1>Ajustes</h1></div>

	<p class="section-label">Voz del timer</p>
	<div class="card">
		{#if voices.length > 0}
			<select class="voice-select"
				value={voices.indexOf(selectedVoice!)}
				onchange={(e) => selectVoice(parseInt(e.currentTarget.value))}>
				{#each voices as v, i}
					<option value={i}>{v.name} ({v.lang})</option>
				{/each}
			</select>
			<button class="btn-test" onclick={testVoice}>Probar</button>
		{:else}
			<p class="hint-small">Voz no disponible en este dispositivo.</p>
		{/if}
	</div>

	<p class="section-label" style="margin-top:24px">Cuenta</p>
	<div class="card">
		<span class="name">{name || '…'}</span>
	</div>
	<div class="pw-row">
		<input type="password" bind:value={newPassword} placeholder="Nueva contraseña" minlength="6" />
		<button class="pw-btn" onclick={changePassword} disabled={pwBusy}>
			{pwBusy ? '…' : 'Cambiar'}
		</button>
	</div>
	{#if pwError}<p class="pw-error">{pwError}</p>{/if}
	{#if pwSuccess}<p class="pw-ok">Contraseña actualizada</p>{/if}

	<div class="sep"></div>
	<button class="btn-logout" onclick={logout}>Cerrar sesión</button>
</Shell>

<style>
	.header { margin-bottom: 16px; }
	h1 { font-size: 1.4rem; font-weight: 700; }

	.section-label {
		font-size: 0.72rem; color: #444; text-transform: uppercase;
		letter-spacing: 1px; margin-bottom: 10px;
	}
	.card {
		background: #1a1a1a; border-radius: 10px;
		padding: 14px 16px; margin-bottom: 8px;
		display: flex; align-items: center; gap: 10px;
	}
	.voice-select {
		flex: 1; background: #0f0f0f; color: #ccc; border: 1px solid #2a2a2a;
		border-radius: 8px; padding: 8px 10px; font-size: 0.85rem;
	}
	.btn-test {
		padding: 8px 14px; font-size: 0.85rem; background: #2a2a2a;
		color: #aaa; border: none; border-radius: 8px; cursor: pointer; white-space: nowrap;
	}
	.hint-small { color: #444; font-size: 0.85rem; }
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
	.btn-logout {
		width: 100%; padding: 12px; background: none; border: 1px solid #2a2a2a;
		color: #555; border-radius: 8px; cursor: pointer; font-size: 0.9rem;
	}
	.btn-logout:hover { color: #ef4444; border-color: #ef4444; }
</style>
