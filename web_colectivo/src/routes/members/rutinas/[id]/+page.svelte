<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import Page from '$lib/Page.svelte';

	type Ex     = { name: string; duration_s: number };
	type Bloque = { name: string; exercises: Ex[] };

	const id = $derived($page.params.id);

	function withDate(n: string): string {
		const d = new Date();
		const dd = String(d.getDate()).padStart(2, '0');
		const mm = String(d.getMonth() + 1).padStart(2, '0');
		return `${n} ${dd}/${mm}/${d.getFullYear()}`;
	}

	function stripDate(n: string): string {
		return n.replace(/ \d{2}\/\d{2}\/\d{4}$/, '').trim();
	}
	let name    = $state('');
	let bloques = $state<Bloque[]>([]);
	let busy    = $state(false);
	let error   = $state('');

	function cloneBloque(b: Bloque): Bloque {
		return { name: b.name, exercises: b.exercises.map(e => ({ name: e.name, duration_s: e.duration_s })) };
	}

	async function load() {
		const { data } = await supabase
			.from('routines')
			.select('name, exercises')
			.eq('id', id)
			.single();
		if (data) { name = stripDate(data.name); bloques = data.exercises as Bloque[]; }
	}

	function addBloque() {
		bloques = [...bloques, { name: '', exercises: [{ name: '', duration_s: 60 }] }];
	}

	function removeBloque(i: number) {
		if (bloques.length > 1) bloques = bloques.filter((_, j) => j !== i);
	}

	function copyBloque(i: number) {
		const b = cloneBloque(bloques[i]);
		if (b.name) b.name += ' (copia)';
		bloques = [...bloques.slice(0, i + 1), b, ...bloques.slice(i + 1)];
	}

	function addEx(bi: number) {
		bloques = bloques.map((b, i) =>
			i === bi ? { ...b, exercises: [...b.exercises, { name: '', duration_s: 60 }] } : b
		);
	}

	function removeEx(bi: number, ei: number) {
		bloques = bloques.map((b, i) =>
			i === bi ? { ...b, exercises: b.exercises.filter((_, j) => j !== ei) } : b
		);
	}

	function setBloqueName(bi: number, val: string) {
		bloques = bloques.map((b, i) => i === bi ? { ...b, name: val } : b);
	}

	function setExName(bi: number, ei: number, val: string) {
		bloques = bloques.map((b, i) =>
			i === bi ? { ...b, exercises: b.exercises.map((e, j) => j === ei ? { ...e, name: val } : e) } : b
		);
	}

	function setExDur(bi: number, ei: number, val: string) {
		const n = Number(val);
		if (!isNaN(n)) bloques = bloques.map((b, i) =>
			i === bi ? { ...b, exercises: b.exercises.map((e, j) => j === ei ? { ...e, duration_s: n } : e) } : b
		);
	}

	async function save() {
		const filtered = bloques
			.map(b => ({ name: b.name.trim(), exercises: b.exercises.filter(e => e.name.trim()) }))
			.filter(b => b.exercises.length > 0);
		if (!name.trim()) { error = 'Ponle nombre'; return; }
		if (filtered.length === 0) { error = 'Al menos un ejercicio'; return; }
		busy = true; error = '';
		const { data: { user } } = await supabase.auth.getUser();
		if (!user) { error = 'Sin sesión activa'; busy = false; return; }
		await supabase.from('routines').delete().eq('id', id);
		const { error: dbErr } = await supabase.from('routines').insert({
			user_id: user.id, name: withDate(name.trim()), exercises: filtered
		});
		if (dbErr) { error = dbErr.message; busy = false; return; }
		goto('/members/rutinas');
	}

	$effect(() => { if (id) load(); });
</script>

<Page title="Editar rutina" back="/rutinas">
	<div class="form">
		<input bind:value={name} placeholder="Nombre de la rutina" />

		{#each bloques as bloque, bi}
			<div class="bloque-form">
				<div class="bloque-form-header">
					<span class="bloque-num">Bloque {bi + 1}</span>
					<input
						value={bloque.name}
						oninput={(e) => setBloqueName(bi, e.currentTarget.value)}
						placeholder="Nombre del bloque"
						class="bloque-name-in"
					/>
					<button class="btn-icon" onclick={() => copyBloque(bi)} title="Copiar bloque">⎘</button>
					{#if bloques.length > 1}
						<button class="btn-icon danger" onclick={() => removeBloque(bi)}>✕</button>
					{/if}
				</div>
				{#each bloque.exercises as ex, ei}
					<div class="ex-row">
						<input
							value={ex.name}
							oninput={(e) => setExName(bi, ei, e.currentTarget.value)}
							placeholder="Ejercicio"
							class="ex-name-in"
						/>
						<input
							type="number"
							value={ex.duration_s}
							oninput={(e) => setExDur(bi, ei, e.currentTarget.value)}
							min="5" max="3600"
							class="ex-dur-in"
						/>
						<span class="dur-unit">s</span>
						{#if bloque.exercises.length > 1}
							<button class="btn-rm" onclick={() => removeEx(bi, ei)}>✕</button>
						{/if}
					</div>
				{/each}
				<button class="btn-secondary small" onclick={() => addEx(bi)}>+ Ejercicio</button>
			</div>
		{/each}

		<button class="btn-secondary" onclick={addBloque}>+ Bloque</button>
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
	.bloque-form {
		background: #1a1a1a; border-radius: 8px; padding: 10px 12px;
		display: flex; flex-direction: column; gap: 8px;
	}
	.bloque-form-header {
		display: flex; align-items: center; gap: 8px; margin-bottom: 2px;
	}
	.bloque-num { font-size: 0.7rem; color: #555; text-transform: uppercase; letter-spacing: 1px; flex: none; white-space: nowrap; }
	.bloque-name-in { flex: 1; font-size: 0.9rem; min-width: 0; width: auto !important; }
	.btn-icon {
		background: none; border: none; color: #555; cursor: pointer;
		font-size: 1rem; padding: 4px 6px; border-radius: 4px; flex: none;
	}
	.btn-icon:hover { color: #ccc; background: #2a2a2a; }
	.btn-icon.danger:hover { color: #ef4444; background: none; }

	.ex-row { display: flex; align-items: center; gap: 8px; }
	.ex-name-in { flex: 1; min-width: 0; width: auto !important; }
	.ex-dur-in { width: 72px !important; flex: none; text-align: center; }
	.dur-unit { font-size: 0.85rem; color: #555; white-space: nowrap; }
	.btn-rm {
		background: none; border: none; color: #444; cursor: pointer;
		font-size: 0.9rem; padding: 4px 6px; flex: none;
	}
	.btn-rm:hover { color: #ef4444; }
	.error { color: #ef4444; font-size: 0.82rem; }
	.actions { margin-top: 8px; }

	.btn-primary {
		width: 100%; padding: 12px 16px; background: #4ade80; color: #0f0f0f;
		border: none; border-radius: 8px; font-size: 0.95rem; font-weight: 700; cursor: pointer;
	}
	.btn-primary:disabled { opacity: 0.5; cursor: default; }
	.btn-secondary {
		padding: 10px 14px; background: #1e1e1e; color: #888;
		border: 1px solid #2a2a2a; border-radius: 8px; font-size: 0.9rem; cursor: pointer;
	}
	.btn-secondary.small { padding: 5px 10px; font-size: 0.78rem; align-self: flex-start; }
</style>
