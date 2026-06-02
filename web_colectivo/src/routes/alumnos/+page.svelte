<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import Shell from '$lib/Shell.svelte';

	type Student = { id: string; name: string };
	let students = $state<Student[]>([]);
	let newName  = $state('');
	let busy     = $state(false);

	async function load() {
		const { data } = await supabase.from('students').select('id, name').order('name');
		students = data ?? [];
	}

	async function add() {
		if (!newName.trim()) return;
		busy = true;
		await supabase.from('students').insert({ name: newName.trim() });
		newName = '';
		await load();
		busy = false;
	}

	async function remove(id: string, name: string) {
		if (!confirm(`¿Borrar a ${name}?`)) return;
		await supabase.from('students').delete().eq('id', id);
		await load();
	}

	$effect(() => { load(); });
</script>

<Shell tab="alumnos">
	<div class="header"><h1>Alumnos</h1></div>

	{#each students as s}
		<div class="list-item">
			<button class="item-btn" onclick={() => goto(`/alumnos/${s.id}`)}>
				<span class="item-title">{s.name}</span>
				<span class="chevron">›</span>
			</button>
			<button class="del" onclick={() => remove(s.id, s.name)}>✕</button>
		</div>
	{/each}

	{#if students.length === 0}
		<p class="hint">Sin alumnos todavía.</p>
	{/if}

	<div class="sep"></div>
	<p class="section-label">Añadir alumno</p>
	<div class="field">
		<input bind:value={newName} placeholder="Nombre del alumno"
			onkeydown={(e) => e.key === 'Enter' && add()} />
	</div>
	<button class="btn-primary" onclick={add} disabled={busy}>Añadir alumno</button>
</Shell>

<style>
	.header { margin-bottom: 16px; }
	h1 { font-size: 1.4rem; font-weight: 700; }
	.list-item {
		display: flex; align-items: center;
		background: #1a1a1a; border-radius: 10px; margin-bottom: 8px;
	}
	.item-btn {
		flex: 1; display: flex; align-items: center;
		padding: 14px 16px; background: none; border: none;
		color: #fff; cursor: pointer; text-align: left; gap: 12px;
	}
	.item-title { flex: 1; font-size: 1rem; font-weight: 600; }
	.chevron { color: #333; font-size: 1.2rem; }
	.del { background: none; border: none; color: #444; cursor: pointer; font-size: 1rem; padding: 4px 12px; }
	.del:hover { color: #ef4444; }
	.sep { height: 1px; background: #1a1a1a; margin: 20px 0; }
	.section-label { font-size: 0.72rem; color: #444; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
	.field { margin-bottom: 12px; }
	.hint { color: #333; text-align: center; padding: 32px 0; }
</style>
