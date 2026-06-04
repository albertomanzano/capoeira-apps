<script lang="ts">
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import Shell from '$lib/Shell.svelte';

	type Ex        = { name: string; duration_s: number };
	type Bloque    = { name: string; exercises: Ex[] };
	type BloqueLog = { name: string; exercises: Ex[]; marks: (number | null)[] };
	type Routine   = { id: string; name: string; exercises: Bloque[] };

	let routines = $state<Routine[]>([]);
	let selected = $state<Routine | null>(null);
	let bloques  = $state<BloqueLog[]>([]);
	let date     = $state(today());
	let saving   = $state(false);

	const isDescanso = (name: string) => /^descanso$/i.test(name.trim());

	function today(): string {
		return new Date().toISOString().slice(0, 10);
	}

	function fmt(s: number): string {
		if (s < 60) return `${s}s`;
		const m = Math.floor(s / 60), r = s % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	function normalize(r: any): Routine {
		const exs = r.exercises ?? [];
		if (exs.length > 0 && exs[0].duration_s !== undefined && !exs[0].exercises) {
			return { ...r, exercises: [{ name: '', exercises: exs }] };
		}
		return r as Routine;
	}

	async function load() {
		const { data } = await supabase
			.from('routines')
			.select('id, name, exercises')
			.order('created_at', { ascending: false });
		routines = (data ?? []).map(normalize) as Routine[];
	}

	function pickRoutine(r: Routine) {
		selected = r;
		bloques = r.exercises.map(b => ({
			...b,
			marks: b.exercises.map(() => null)
		}));
	}

	function setMark(bi: number, ei: number, raw: string) {
		bloques[bi].marks[ei] = raw ? Number(raw) : null;
	}

	async function save() {
		if (!selected) return;
		saving = true;
		const { data: { user } } = await supabase.auth.getUser();
		await supabase.from('training_logs').insert({
			user_id: user!.id,
			routine_id: selected.id,
			routine_name: selected.name,
			exercises: bloques,
			date
		});
		goto('/members/historial');
	}

	$effect(() => { load(); });
</script>

<Shell tab="historial">
	<div class="header">
		<button class="btn-back" onclick={() => goto('/members/historial')}>← Historial</button>
		<h1>Nueva entrada</h1>
	</div>

	<label class="field">
		<span class="label">Fecha</span>
		<input type="date" bind:value={date} class="date-input" />
	</label>

	{#if !selected}
		<p class="section-label">Elige una rutina</p>
		{#if routines.length === 0}
			<p class="hint">Sin rutinas. Crea una primero.</p>
		{:else}
			<div class="routine-list">
				{#each routines as r}
					<button class="routine-item" onclick={() => pickRoutine(r)}>
						{r.name}
					</button>
				{/each}
			</div>
		{/if}
	{:else}
		<div class="selected-header">
			<span class="selected-name">{selected.name}</span>
			<button class="btn-change" onclick={() => { selected = null; bloques = []; }}>Cambiar</button>
		</div>

		<div class="bloques">
			{#each bloques as bloque, bi}
				<div class="bloque">
					<p class="bloque-name">{bloque.name || `Bloque ${bi + 1}`}</p>
					{#each bloque.exercises as ex, ei}
						{#if !isDescanso(ex.name)}
							<div class="ex-row">
								<span class="ex-name">{ex.name}</span>
								<span class="ex-dur">{fmt(ex.duration_s)}</span>
								<input
									type="number"
									inputmode="numeric"
									placeholder="—"
									value={bloque.marks[ei] ?? ''}
									oninput={(e) => setMark(bi, ei, e.currentTarget.value)}
									class="mark-edit"
								/>
							</div>
						{/if}
					{/each}
				</div>
			{/each}
		</div>

		<button class="btn-save" onclick={save} disabled={saving}>
			{saving ? 'Guardando…' : 'Guardar entrada'}
		</button>
	{/if}
</Shell>

<style>
	.header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
	.btn-back {
		background: none; border: none; color: #555; cursor: pointer;
		font-size: 0.85rem; padding: 0; flex: none;
	}
	.btn-back:hover { color: #ccc; }
	h1 { font-size: 1.2rem; font-weight: 700; }

	.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 20px; }
	.label { font-size: 0.72rem; color: #555; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700; }
	.date-input {
		background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px;
		color: #ccc; font-size: 0.95rem; padding: 10px 12px;
		width: 100%; box-sizing: border-box;
	}
	.date-input:focus { border-color: #4ade80; outline: none; }

	.section-label {
		font-size: 0.72rem; color: #555; text-transform: uppercase;
		letter-spacing: 0.8px; font-weight: 700; margin-bottom: 10px;
	}
	.routine-list { display: flex; flex-direction: column; gap: 6px; }
	.routine-item {
		background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px;
		color: #ccc; text-align: left; padding: 14px 16px; cursor: pointer;
		font-size: 0.9rem; transition: background 0.15s;
	}
	.routine-item:hover { background: #222; border-color: #3a3a3a; }

	.selected-header {
		display: flex; align-items: center; justify-content: space-between;
		margin-bottom: 20px;
	}
	.selected-name { font-size: 0.95rem; font-weight: 700; color: #ccc; }
	.btn-change {
		background: none; border: none; color: #555; cursor: pointer;
		font-size: 0.8rem; padding: 0;
	}
	.btn-change:hover { color: #ccc; }

	.bloques { display: flex; flex-direction: column; gap: 20px; margin-bottom: 28px; }
	.bloque { display: flex; flex-direction: column; gap: 6px; }
	.bloque-name {
		font-size: 0.72rem; color: #555; text-transform: uppercase;
		letter-spacing: 0.8px; font-weight: 700; margin-bottom: 4px;
	}
	.ex-row { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; }
	.ex-name { flex: 1; color: #aaa; }
	.ex-dur  { color: #444; font-size: 0.78rem; width: 40px; text-align: right; }
	.mark-edit {
		width: 60px; text-align: center; font-size: 1rem; font-weight: 700;
		padding: 6px 8px; border-radius: 6px; color: #4ade80;
		background: #0f0f0f; border: 1px solid #2a2a2a;
		-moz-appearance: textfield;
	}
	.mark-edit::-webkit-outer-spin-button,
	.mark-edit::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
	.mark-edit:focus { border-color: #4ade80; outline: none; }

	.btn-save {
		width: 100%; padding: 14px; border-radius: 10px;
		background: #4ade80; color: #000; border: none;
		font-size: 1rem; font-weight: 700; cursor: pointer;
		transition: opacity 0.15s;
	}
	.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

	.hint { color: #333; text-align: center; padding: 20px 0; font-size: 0.9rem; }
</style>
