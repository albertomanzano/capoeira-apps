<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import Shell from '$lib/Shell.svelte';

	type Ex      = { name: string; duration_s: number };
	type Routine = { id: string; name: string; exercises: Ex[]; created_at: string };

	let routines = $state<Routine[]>([]);
	let creating = $state(false);
	let newName  = $state('');
	let newExs   = $state<Ex[]>([{ name: '', duration_s: 60 }]);
	let busy     = $state(false);
	let error    = $state('');

	function fmt(s: number): string {
		if (s < 60) return `${s}s`;
		const m = Math.floor(s / 60), r = s % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	async function load() {
		const { data } = await supabase
			.from('routines')
			.select('id, name, exercises, created_at')
			.order('created_at', { ascending: false });
		routines = (data ?? []) as Routine[];
	}

	function startCreate() {
		creating = true; newName = ''; newExs = [{ name: '', duration_s: 60 }]; error = '';
	}

	function addEx() { newExs = [...newExs, { name: '', duration_s: 60 }]; }
	function removeEx(i: number) { newExs = newExs.filter((_, j) => j !== i); }

	async function saveNew() {
		const exs = newExs.filter(e => e.name.trim());
		if (!newName.trim()) { error = 'Ponle nombre a la rutina'; return; }
		if (exs.length === 0) { error = 'Añade al menos un ejercicio'; return; }
		busy = true; error = '';
		const { data: { user } } = await supabase.auth.getUser();
		await supabase.from('routines').insert({ user_id: user!.id, name: newName.trim(), exercises: exs });
		creating = false;
		await load();
		busy = false;
	}

	async function remove(id: string, name: string) {
		if (!confirm(`¿Borrar "${name}"?`)) return;
		await supabase.from('routines').delete().eq('id', id);
		await load();
	}

	$effect(() => { load(); });
</script>

<Shell tab="rutinas">
	<div class="header">
		<h1>Rutinas</h1>
		{#if !creating}
			<button class="btn-add" onclick={startCreate}>+ Nueva</button>
		{/if}
	</div>

	{#if creating}
		<div class="form-card">
			<input bind:value={newName} placeholder="Nombre de la rutina" />

			<p class="form-label">Ejercicios</p>
			{#each newExs as ex, i}
				<div class="ex-row">
					<input bind:value={ex.name} placeholder="Nombre" class="ex-name-in" />
					<input type="number" bind:value={ex.duration_s} min="5" max="3600" class="ex-dur-in" />
					<span class="dur-unit">s</span>
					<button class="btn-rm" onclick={() => removeEx(i)}>✕</button>
				</div>
			{/each}
			<button class="btn-secondary" onclick={addEx}>+ Ejercicio</button>
			{#if error}<p class="error">{error}</p>{/if}
			<button class="btn-primary" onclick={saveNew} disabled={busy}>
				{busy ? 'Guardando…' : 'Guardar rutina'}
			</button>
			<button class="btn-secondary" onclick={() => creating = false}>Cancelar</button>
		</div>
	{/if}

	{#each routines as r}
		<div class="routine-card">
			<button class="routine-main" onclick={() => goto(`/rutinas/${r.id}`)}>
				<span class="routine-name">{r.name}</span>
				<span class="routine-meta">{r.exercises.length} ejercicio{r.exercises.length !== 1 ? 's' : ''}</span>
				<div class="ex-pills">
					{#each r.exercises as ex}
						<span class="pill">{ex.name}<span class="pill-dur"> {fmt(ex.duration_s)}</span></span>
					{/each}
				</div>
			</button>
			<button class="btn-del" onclick={() => remove(r.id, r.name)}>✕</button>
		</div>
	{/each}

	{#if routines.length === 0 && !creating}
		<p class="hint">Sin rutinas todavía. Crea la primera.</p>
	{/if}
</Shell>

<style>
	.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
	h1 { font-size: 1.4rem; font-weight: 700; }
	.btn-add {
		padding: 8px 16px; background: #4ade80; color: #0f0f0f;
		border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 700; cursor: pointer;
	}
	.form-card {
		background: #141414; border: 1px solid #2a2a2a; border-radius: 12px;
		padding: 16px; margin-bottom: 16px; display: flex; flex-direction: column; gap: 10px;
	}
	.form-label { font-size: 0.72rem; color: #444; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
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

	.routine-card {
		display: flex; align-items: flex-start;
		background: #1a1a1a; border-radius: 10px; margin-bottom: 8px; overflow: hidden;
	}
	.routine-main {
		flex: 1; display: flex; flex-direction: column; align-items: flex-start; gap: 6px;
		padding: 14px 16px; background: none; border: none; color: #fff; cursor: pointer; text-align: left;
	}
	.routine-name { font-size: 1rem; font-weight: 700; }
	.routine-meta { font-size: 0.72rem; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }
	.ex-pills { display: flex; flex-wrap: wrap; gap: 6px; }
	.pill {
		font-size: 0.78rem; background: #222; border-radius: 6px;
		padding: 3px 8px; color: #aaa;
	}
	.pill-dur { color: #555; }
	.btn-del {
		background: none; border: none; color: #333; cursor: pointer;
		font-size: 0.9rem; padding: 14px 12px; align-self: stretch;
		display: flex; align-items: center;
	}
	.btn-del:hover { color: #ef4444; }
	.hint { color: #333; text-align: center; padding: 40px 0; font-size: 0.9rem; }
</style>
