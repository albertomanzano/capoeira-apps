<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import Page from '$lib/Page.svelte';

	type Ex = { name: string; duration_s: number };

	const id = $derived($page.params.id);
	let name  = $state('');
	let exs   = $state<Ex[]>([]);
	let busy  = $state(false);
	let error = $state('');

	async function load() {
		const { data } = await supabase
			.from('routines')
			.select('name, exercises')
			.eq('id', id)
			.single();
		if (data) { name = data.name; exs = data.exercises as Ex[]; }
	}

	function addEx() { exs = [...exs, { name: '', duration_s: 60 }]; }
	function removeEx(i: number) { exs = exs.filter((_, j) => j !== i); }

	async function save() {
		const filtered = exs.filter(e => e.name.trim());
		if (!name.trim()) { error = 'Ponle nombre'; return; }
		if (filtered.length === 0) { error = 'Al menos un ejercicio'; return; }
		busy = true; error = '';
		await supabase.from('routines').update({ name: name.trim(), exercises: filtered }).eq('id', id);
		goto('/rutinas');
	}

	$effect(() => { if (id) load(); });
</script>

<Page title="Editar rutina" back="/rutinas">
	<div class="form">
		<input bind:value={name} placeholder="Nombre de la rutina" />

		<p class="form-label">Ejercicios</p>
		{#each exs as ex, i}
			<div class="ex-row">
				<input bind:value={ex.name} placeholder="Nombre" class="ex-name-in" />
				<input type="number" bind:value={ex.duration_s} min="5" max="3600" class="ex-dur-in" />
				<span class="dur-unit">s</span>
				<button class="btn-rm" onclick={() => removeEx(i)}>✕</button>
			</div>
		{/each}
		<button class="btn-secondary" onclick={addEx}>+ Ejercicio</button>
		{#if error}<p class="error">{error}</p>{/if}
		<div class="actions">
			<button class="btn-primary" onclick={save} disabled={busy}>
				{busy ? 'Guardando…' : 'Guardar cambios'}
			</button>
		</div>
	</div>
</Page>

<style>
	.form { display: flex; flex-direction: column; gap: 10px; }
	.form-label { font-size: 0.72rem; color: #444; text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; }
	.ex-row { display: flex; align-items: center; gap: 8px; }
	.ex-name-in { flex: 1; }
	.ex-dur-in { width: 72px; flex: none; text-align: center; }
	.dur-unit { font-size: 0.85rem; color: #555; white-space: nowrap; }
	.btn-rm {
		background: none; border: none; color: #444; cursor: pointer;
		font-size: 0.9rem; padding: 4px 6px; flex: none;
	}
	.btn-rm:hover { color: #ef4444; }
	.error { color: #ef4444; font-size: 0.82rem; }
	.actions { margin-top: 8px; }
</style>
