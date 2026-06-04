<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import Shell from '$lib/Shell.svelte';

	type Ex      = { name: string; duration_s: number };
	type Bloque  = { name: string; exercises: Ex[] };
	type Routine = { id: string; name: string; exercises: Bloque[]; created_at: string };

	let routines   = $state<Routine[]>([]);
	let creating   = $state(false);
	let newName    = $state('');
	let newBloques = $state<Bloque[]>([{ name: '', exercises: [{ name: '', duration_s: 60 }] }]);
	let busy       = $state(false);
	let error      = $state('');
	let expanded   = $state<Set<string>>(new Set());

	function withDate(n: string): string {
		const d = new Date();
		const dd = String(d.getDate()).padStart(2, '0');
		const mm = String(d.getMonth() + 1).padStart(2, '0');
		return `${n} ${dd}/${mm}/${d.getFullYear()}`;
	}

	function fmt(s: number): string {
		if (s < 60) return `${s}s`;
		const m = Math.floor(s / 60), r = s % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	const isDescanso = (name: string) => /^descanso$/i.test(name.trim());

	function totalExs(bloques: Bloque[]) {
		return bloques.reduce((s, b) => s + b.exercises.filter(e => !isDescanso(e.name)).length, 0);
	}

	function totalDuration(bloques: Bloque[]): string {
		const secs = bloques.reduce((s, b) => s + b.exercises.reduce((bs, e) => bs + e.duration_s, 0), 0);
		if (secs < 60) return `${secs}s`;
		const m = Math.floor(secs / 60), r = secs % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	function cloneBloque(b: Bloque): Bloque {
		return { name: b.name, exercises: b.exercises.map(e => ({ name: e.name, duration_s: e.duration_s })) };
	}

	let loadError = $state('');

	function normalize(r: any): Routine {
		const exs = r.exercises ?? [];
		if (exs.length > 0 && exs[0].duration_s !== undefined && !exs[0].exercises) {
			return { ...r, exercises: [{ name: '', exercises: exs }] };
		}
		return r as Routine;
	}

	async function load() {
		const { data, error: loadErr } = await supabase
			.from('routines')
			.select('id, name, exercises, created_at')
			.order('created_at', { ascending: false });
		if (loadErr) { loadError = loadErr.message; return; }
		loadError = '';
		routines = (data ?? []).map(normalize) as Routine[];
	}

	function toggle(id: string) {
		const s = new Set(expanded);
		if (s.has(id)) s.delete(id); else s.add(id);
		expanded = s;
	}

	function startCreate() {
		creating = true; newName = '';
		newBloques = [{ name: '', exercises: [{ name: '', duration_s: 60 }] }];
		error = '';
	}

	function addBloque() {
		newBloques = [...newBloques, { name: '', exercises: [{ name: '', duration_s: 60 }] }];
	}

	function removeBloque(i: number) {
		if (newBloques.length > 1) newBloques = newBloques.filter((_, j) => j !== i);
	}

	function copyBloque(i: number) {
		const b = cloneBloque(newBloques[i]);
		if (b.name) b.name += ' (copia)';
		newBloques = [...newBloques.slice(0, i + 1), b, ...newBloques.slice(i + 1)];
	}

	function addEx(bi: number) {
		newBloques = newBloques.map((b, i) =>
			i === bi ? { ...b, exercises: [...b.exercises, { name: '', duration_s: 60 }] } : b
		);
	}

	function removeEx(bi: number, ei: number) {
		newBloques = newBloques.map((b, i) =>
			i === bi ? { ...b, exercises: b.exercises.filter((_, j) => j !== ei) } : b
		);
	}

	function setBloqueName(bi: number, val: string) {
		newBloques = newBloques.map((b, i) => i === bi ? { ...b, name: val } : b);
	}

	function setExName(bi: number, ei: number, val: string) {
		newBloques = newBloques.map((b, i) =>
			i === bi ? { ...b, exercises: b.exercises.map((e, j) => j === ei ? { ...e, name: val } : e) } : b
		);
	}

	function setExDur(bi: number, ei: number, val: string) {
		const n = Number(val);
		if (!isNaN(n)) newBloques = newBloques.map((b, i) =>
			i === bi ? { ...b, exercises: b.exercises.map((e, j) => j === ei ? { ...e, duration_s: n } : e) } : b
		);
	}

	async function saveNew() {
		const bloques = newBloques
			.map(b => ({ name: b.name.trim(), exercises: b.exercises.filter(e => e.name.trim()) }))
			.filter(b => b.exercises.length > 0);
		if (!newName.trim()) { error = 'Ponle nombre a la rutina'; return; }
		if (bloques.length === 0) { error = 'Añade al menos un ejercicio'; return; }
		busy = true; error = '';
		try {
			const { data: authData } = await supabase.auth.getUser();
			if (!authData.user) { error = 'Sin sesión activa. Recarga la página.'; busy = false; return; }
			const { error: dbErr } = await supabase.from('routines').insert({
				user_id: authData.user.id, name: withDate(newName.trim()), exercises: bloques
			});
			if (dbErr) { error = dbErr.message; busy = false; return; }
			creating = false;
			await load();
		} catch (e: any) {
			error = e?.message ?? 'Error desconocido';
		}
		busy = false;
	}

	async function copyRoutine(r: Routine) {
		const { data: { user } } = await supabase.auth.getUser();
		await supabase.from('routines').insert({
			user_id: user!.id, name: `${r.name} (copia)`, exercises: r.exercises
		});
		await load();
	}

	async function remove(id: string, name: string) {
		if (!confirm(`¿Borrar "${name}"?`)) return;
		await supabase.from('routines').delete().eq('id', id);
		await load();
	}

	function launchTimer(bloque: Bloque, routineId: string, routineName: string) {
		localStorage.removeItem('capoeira_timer_rutina');
		localStorage.setItem('capoeira_timer_bloque', JSON.stringify(cloneBloque(bloque)));
		localStorage.setItem('capoeira_timer_meta', JSON.stringify({ routine_id: routineId, routine_name: routineName }));
		goto('/members/timer');
	}

	function launchTimerRutina(r: Routine) {
		localStorage.removeItem('capoeira_timer_bloque');
		localStorage.setItem('capoeira_timer_rutina', JSON.stringify({ name: r.name, exercises: r.exercises }));
		localStorage.setItem('capoeira_timer_meta', JSON.stringify({ routine_id: r.id, routine_name: r.name }));
		goto('/members/timer');
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

			{#each newBloques as bloque, bi}
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
						{#if newBloques.length > 1}
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
			<button class="btn-primary" onclick={saveNew} disabled={busy}>
				{busy ? 'Guardando…' : 'Guardar rutina'}
			</button>
			<button class="btn-secondary" onclick={() => creating = false}>Cancelar</button>
		</div>
	{/if}

	{#if loadError}<p class="load-error">Error al cargar: {loadError}</p>{/if}

	{#each routines as r}
		<div class="routine-card" class:open={expanded.has(r.id)}>
			<button class="routine-summary" onclick={() => toggle(r.id)}>
				<span class="chevron">{expanded.has(r.id) ? '▾' : '▸'}</span>
				<span class="routine-name">{r.name}</span>
				<span class="routine-meta">
					{r.exercises.length} bl · {totalExs(r.exercises)} ej · {totalDuration(r.exercises)}
				</span>
			</button>
			<div class="routine-actions">
				<button class="btn-play" onclick={(e) => { e.stopPropagation(); launchTimerRutina(r); }} title="Timer rutina completa">▶</button>
				<button class="btn-icon" onclick={() => copyRoutine(r)} title="Copiar rutina">⎘</button>
					<button class="btn-icon danger" onclick={() => remove(r.id, r.name)}>✕</button>
			</div>
		</div>
		{#if expanded.has(r.id)}
			<div class="bloques-list">
				{#each r.exercises as bloque, bi}
					<div class="bloque-item">
						<div class="bloque-header">
							<span class="bloque-title">{bloque.name || `Bloque ${bi + 1}`}</span>
							<span class="bloque-count">{bloque.exercises.filter(e => !isDescanso(e.name)).length} ej</span>
							<button class="btn-play" onclick={() => launchTimer(bloque, r.id, r.name)}>▶</button>
						</div>
						<div class="ex-pills">
							{#each bloque.exercises.filter(e => !isDescanso(e.name)) as ex}
								<span class="pill">{ex.name}<span class="pill-dur"> {fmt(ex.duration_s)}</span></span>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		{/if}
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

	/* form */
	.form-card {
		background: #141414; border: 1px solid #2a2a2a; border-radius: 12px;
		padding: 16px; margin-bottom: 16px; display: flex; flex-direction: column; gap: 10px;
	}
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

	/* list */
	.routine-card {
		display: flex; align-items: center;
		background: #1a1a1a; border-radius: 10px; margin-bottom: 4px; overflow: hidden;
	}
	.routine-card.open { border-radius: 10px 10px 0 0; margin-bottom: 0; }
	.routine-summary {
		flex: 1; display: flex; align-items: center; gap: 10px;
		padding: 14px 16px; background: none; border: none; color: #fff; cursor: pointer; text-align: left;
		min-width: 0;
	}
	.chevron { font-size: 0.75rem; color: #555; flex: none; }
	.routine-name { font-size: 1rem; font-weight: 700; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.routine-meta { font-size: 0.72rem; color: #555; flex: none; white-space: nowrap; }
	.routine-actions { display: flex; align-items: center; padding-right: 8px; gap: 2px; }

	.bloques-list {
		background: #141414; border-radius: 0 0 10px 10px;
		padding: 8px 12px 12px; margin-bottom: 10px;
		display: flex; flex-direction: column; gap: 10px;
	}
	.bloque-item { display: flex; flex-direction: column; gap: 6px; }
	.bloque-header { display: flex; align-items: center; gap: 8px; }
	.bloque-title { font-size: 0.85rem; font-weight: 700; color: #ccc; flex: 1; }
	.bloque-count { font-size: 0.72rem; color: #444; }
	.btn-play {
		background: none; border: 1px solid #2a4a2a; color: #4ade80; cursor: pointer;
		font-size: 0.78rem; padding: 3px 8px; border-radius: 6px; flex: none;
	}
	.btn-play:hover { background: #1a2e1a; }

	.ex-pills { display: flex; flex-wrap: wrap; gap: 5px; padding-left: 2px; }
	.pill {
		font-size: 0.75rem; background: #1e1e1e; border-radius: 6px;
		padding: 3px 8px; color: #888; border: 1px solid #2a2a2a;
	}
	.pill-dur { color: #444; }

	.load-error { color: #ef4444; font-size: 0.82rem; padding: 8px 0; }
	.hint { color: #333; text-align: center; padding: 40px 0; font-size: 0.9rem; }

	.btn-primary {
		padding: 12px 16px; background: #4ade80; color: #0f0f0f;
		border: none; border-radius: 8px; font-size: 0.95rem; font-weight: 700; cursor: pointer;
	}
	.btn-primary:disabled { opacity: 0.5; cursor: default; }
	.btn-secondary {
		padding: 10px 14px; background: #1a1a1a; color: #888;
		border: 1px solid #2a2a2a; border-radius: 8px; font-size: 0.9rem; cursor: pointer;
	}
	.btn-secondary.small { padding: 5px 10px; font-size: 0.78rem; align-self: flex-start; }
</style>
