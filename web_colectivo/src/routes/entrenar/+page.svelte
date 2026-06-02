<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { goto } from '$app/navigation';
	import Shell from '$lib/Shell.svelte';

	type Ex      = { name: string; duration_s: number };
	type Bloque  = { name: string; exercises: Ex[] };
	type Routine = { id: string; name: string; exercises: Bloque[] };

	let routines      = $state<Routine[]>([]);
	let selected      = $state<Routine | null>(null);
	let marksByBloque = $state<(number | null)[][]>([]);
	let date          = $state(new Date().toISOString().split('T')[0]);
	let busy          = $state(false);
	let saved         = $state(false);

	function fmt(s: number): string {
		if (s < 60) return `${s}s`;
		const m = Math.floor(s / 60), r = s % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	function totalExs(bloques: Bloque[]) {
		return bloques.reduce((s, b) => s + b.exercises.length, 0);
	}

	async function load() {
		const { data } = await supabase
			.from('routines')
			.select('id, name, exercises')
			.order('created_at', { ascending: false });
		routines = (data ?? []) as Routine[];
	}

	function pick(r: Routine) {
		selected = r;
		marksByBloque = r.exercises.map(b => b.exercises.map(() => null));
		saved = false;
	}

	function setMark(bi: number, ei: number, raw: string) {
		marksByBloque[bi][ei] = raw ? Number(raw) : null;
	}

	async function saveLog() {
		if (!selected) return;
		busy = true;
		const { data: { user } } = await supabase.auth.getUser();
		const bloques = selected.exercises.map((b, bi) => ({
			name: b.name,
			exercises: b.exercises,
			marks: marksByBloque[bi],
		}));
		await supabase.from('training_logs').insert({
			user_id:      user!.id,
			routine_id:   selected.id,
			routine_name: selected.name,
			exercises:    bloques,
			marks:        [],
			date,
		});
		saved = true;
		busy = false;
	}

	function reset() { selected = null; marksByBloque = []; saved = false; }

	$effect(() => { load(); });
</script>

<Shell tab="entrenar">
	{#if saved}
		<div class="saved-wrap">
			<p class="saved-icon">✓</p>
			<p class="saved-title">¡Guardado!</p>
			<button class="btn-primary" onclick={reset}>Otro entreno</button>
			<button class="btn-secondary" onclick={() => goto('/historial')}>Ver historial</button>
		</div>

	{:else if selected}
		<div class="session-header">
			<button class="back-btn" onclick={reset}>← {selected.name}</button>
			<input type="date" bind:value={date} class="date-input" />
		</div>

		{#each selected.exercises as bloque, bi}
			<p class="bloque-label">{bloque.name || `Bloque ${bi + 1}`}</p>
			{#each bloque.exercises as ex, ei}
				<div class="ex-card">
					<div class="ex-info">
						<span class="ex-name">{ex.name}</span>
						<span class="ex-dur">{fmt(ex.duration_s)}</span>
					</div>
					<input
						type="number"
						inputmode="numeric"
						placeholder="—"
						value={marksByBloque[bi]?.[ei] ?? ''}
						oninput={(e) => setMark(bi, ei, e.currentTarget.value)}
						class="mark-input"
					/>
				</div>
			{/each}
		{/each}

		<button class="btn-primary" style="margin-top:16px" onclick={saveLog} disabled={busy}>
			{busy ? 'Guardando…' : 'Guardar entreno'}
		</button>

	{:else}
		<div class="header"><h1>Entrenar</h1></div>
		{#if routines.length === 0}
			<p class="hint">Sin rutinas. <a href="/rutinas">Crea una primero.</a></p>
		{:else}
			<p class="section-label">Elige una rutina</p>
			{#each routines as r}
				<button class="routine-btn" onclick={() => pick(r)}>
					<div>
						<span class="routine-name">{r.name}</span>
						<span class="routine-meta">
							{r.exercises.length} bloque{r.exercises.length !== 1 ? 's' : ''} · {totalExs(r.exercises)} ejercicio{totalExs(r.exercises) !== 1 ? 's' : ''}
						</span>
					</div>
					<span class="chevron">›</span>
				</button>
			{/each}
		{/if}
	{/if}
</Shell>

<style>
	.header { margin-bottom: 16px; }
	h1 { font-size: 1.4rem; font-weight: 700; }
	.section-label { font-size: 0.72rem; color: #444; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }

	.routine-btn {
		display: flex; align-items: center; justify-content: space-between;
		width: 100%; padding: 16px; background: #1a1a1a; border: none;
		border-radius: 10px; color: #fff; cursor: pointer; text-align: left;
		margin-bottom: 8px;
	}
	.routine-btn > div { display: flex; flex-direction: column; gap: 4px; }
	.routine-name { font-size: 1rem; font-weight: 700; }
	.routine-meta { font-size: 0.72rem; color: #555; }
	.chevron { color: #333; font-size: 1.4rem; }

	.session-header {
		display: flex; align-items: center; justify-content: space-between;
		margin-bottom: 16px; gap: 12px;
	}
	.back-btn {
		background: none; border: none; color: #888; cursor: pointer;
		font-size: 0.95rem; padding: 0; text-align: left; flex: 1;
	}
	.date-input {
		width: auto; flex: none; font-size: 0.85rem;
		padding: 8px 10px; border-radius: 8px;
		background: #1a1a1a; border: 1px solid #2a2a2a; color: #fff;
	}

	.bloque-label {
		font-size: 0.72rem; color: #555; text-transform: uppercase;
		letter-spacing: 0.8px; font-weight: 700;
		margin: 14px 0 6px; padding-left: 2px;
	}
	.ex-card {
		display: flex; align-items: center; justify-content: space-between;
		background: #1a1a1a; border-radius: 10px; padding: 14px 16px;
		margin-bottom: 6px; gap: 12px;
	}
	.ex-info { display: flex; flex-direction: column; gap: 4px; flex: 1; }
	.ex-name { font-size: 1rem; font-weight: 600; }
	.ex-dur  { font-size: 0.75rem; color: #555; }
	.mark-input {
		width: 80px; flex: none; text-align: center;
		font-size: 1.1rem; font-weight: 700;
		padding: 10px 8px; border-radius: 8px;
		background: #0f0f0f; border: 1px solid #2a2a2a; color: #fff;
	}

	.saved-wrap {
		display: flex; flex-direction: column; align-items: center;
		gap: 12px; padding-top: 60px; text-align: center;
	}
	.saved-icon  { font-size: 3rem; color: #4ade80; }
	.saved-title { font-size: 1.6rem; font-weight: 700; color: #4ade80; }

	.btn-primary {
		width: 100%; padding: 12px 16px; background: #4ade80; color: #0f0f0f;
		border: none; border-radius: 8px; font-size: 0.95rem; font-weight: 700; cursor: pointer;
	}
	.btn-primary:disabled { opacity: 0.5; cursor: default; }
	.btn-secondary {
		width: 100%; padding: 10px 14px; background: #1a1a1a; color: #888;
		border: 1px solid #2a2a2a; border-radius: 8px; font-size: 0.9rem; cursor: pointer;
	}
	.hint { color: #333; text-align: center; padding: 40px 0; font-size: 0.9rem; }
	.hint a { color: #4ade80; text-decoration: none; }
</style>
