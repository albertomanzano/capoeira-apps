<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import Shell from '$lib/Shell.svelte';

	type Ex        = { name: string; duration_s: number };
	type BloqueLog = { name: string; exercises: Ex[]; marks: (number | null)[] };
	type Log = { id: string; date: string; routine_name: string; exercises: BloqueLog[] };

	let log = $state<Log | null>(null);

	const isDescanso = (name: string) => /^descanso$/i.test(name.trim());

	function fmt(s: number): string {
		if (s < 60) return `${s}s`;
		const m = Math.floor(s / 60), r = s % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	function fmtDate(d: string): string {
		const [y, m, day] = d.split('-');
		return `${day}/${m}/${y.slice(2)}`;
	}

	async function load(id: string) {
		const { data } = await supabase
			.from('training_logs')
			.select('id, date, routine_name, exercises')
			.eq('id', id)
			.single();
		log = data as Log ?? null;
	}

	function setMark(bi: number, ei: number, raw: string) {
		if (!log) return;
		if (!log.exercises[bi].marks) {
			log.exercises[bi].marks = log.exercises[bi].exercises.map(() => null);
		}
		while (log.exercises[bi].marks.length <= ei) log.exercises[bi].marks.push(null);
		log.exercises[bi].marks[ei] = raw ? Number(raw) : null;
	}

	async function saveMark() {
		if (!log) return;
		await supabase
			.from('training_logs')
			.update({ exercises: log.exercises })
			.eq('id', log.id);
	}

	async function remove() {
		if (!log) return;
		if (!confirm('¿Borrar esta entrada?')) return;
		await supabase.from('training_logs').delete().eq('id', log.id);
		goto('/members/historial');
	}

	$effect(() => { load($page.params.id); });
</script>

<Shell tab="historial">
	<div class="header">
		<button class="btn-back" onclick={() => goto('/members/historial')}>← Historial</button>
	</div>

	{#if !log}
		<p class="hint">Cargando…</p>
	{:else}
		<div class="meta">
			<span class="routine-name">{log.routine_name}</span>
			<span class="log-date">{fmtDate(log.date)}</span>
		</div>

		<div class="bloques">
			{#each log.exercises as bloque, bi}
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
									value={bloque.marks?.[ei] ?? ''}
									oninput={(e) => setMark(bi, ei, e.currentTarget.value)}
									onblur={saveMark}
									class="mark-edit"
								/>
							</div>
						{/if}
					{/each}
				</div>
			{/each}
		</div>

		<button class="btn-del" onclick={remove}>Borrar entrada</button>
	{/if}
</Shell>

<style>
	.header { margin-bottom: 16px; }
	.btn-back {
		background: none; border: none; color: #555; cursor: pointer;
		font-size: 0.85rem; padding: 0;
	}
	.btn-back:hover { color: var(--text); }

	.meta {
		display: flex; flex-direction: column; gap: 4px;
		margin-bottom: 20px;
	}
	.routine-name { font-size: 1.1rem; font-weight: 700; color: var(--text); }
	.log-date { font-size: 0.8rem; color: #555; }

	.bloques { display: flex; flex-direction: column; gap: 20px; margin-bottom: 32px; }
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
		padding: 6px 8px; border-radius: 6px; color: var(--accent);
		background: var(--bg); border: 1px solid var(--border);
		-moz-appearance: textfield;
	}
	.mark-edit::-webkit-outer-spin-button,
	.mark-edit::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
	.mark-edit:focus { border-color: var(--accent); outline: none; }

	.btn-del {
		width: 100%; padding: 12px; border-radius: 8px;
		background: none; border: 1px solid var(--border); color: #444;
		cursor: pointer; font-size: 0.85rem; transition: all 0.15s;
	}
	.btn-del:hover { border-color: #ef4444; color: #ef4444; }

	.hint { color: #333; text-align: center; padding: 40px 0; font-size: 0.9rem; }
</style>
