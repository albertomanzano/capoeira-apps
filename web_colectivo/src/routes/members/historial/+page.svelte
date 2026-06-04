<script lang="ts">
	import { supabase } from '$lib/supabase';
	import Shell from '$lib/Shell.svelte';

	type Ex        = { name: string; duration_s: number };
	type BloqueLog = { name: string; exercises: Ex[]; marks: (number | null)[] };
	type Log = {
		id: string; date: string; routine_name: string;
		exercises: BloqueLog[];
	};

	let logs     = $state<Log[]>([]);
	let expanded = $state<Set<string>>(new Set());

	function fmt(s: number): string {
		if (s < 60) return `${s}s`;
		const m = Math.floor(s / 60), r = s % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	function fmtDate(d: string): string {
		const [y, m, day] = d.split('-');
		return `${day}/${m}/${y.slice(2)}`;
	}

	const isDescanso = (name: string) => /^descanso$/i.test(name.trim());

	function totalExs(bloques: BloqueLog[]) {
		return bloques.reduce((s, b) => s + b.exercises.filter(e => !isDescanso(e.name)).length, 0);
	}

	function totalDuration(bloques: BloqueLog[]): string {
		const secs = bloques.reduce((s, b) => s + b.exercises.reduce((bs, e) => bs + e.duration_s, 0), 0);
		if (secs < 60) return `${secs}s`;
		const m = Math.floor(secs / 60), r = secs % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	async function load() {
		const { data } = await supabase
			.from('training_logs')
			.select('id, date, routine_name, exercises')
			.order('date', { ascending: false })
			.limit(60);
		logs = (data ?? []) as Log[];
	}

	function toggle(id: string) {
		const s = new Set(expanded);
		if (s.has(id)) s.delete(id); else s.add(id);
		expanded = s;
	}

	async function remove(id: string, e: MouseEvent) {
		e.stopPropagation();
		if (!confirm('¿Borrar esta entrada?')) return;
		await supabase.from('training_logs').delete().eq('id', id);
		await load();
	}

	function setMark(log: Log, bi: number, ei: number, raw: string) {
		if (!log.exercises[bi].marks) {
			log.exercises[bi].marks = log.exercises[bi].exercises.map(() => null);
		}
		while (log.exercises[bi].marks.length <= ei) log.exercises[bi].marks.push(null);
		log.exercises[bi].marks[ei] = raw ? Number(raw) : null;
	}

	async function saveMark(log: Log) {
		await supabase
			.from('training_logs')
			.update({ exercises: log.exercises })
			.eq('id', log.id);
	}

	$effect(() => { load(); });
</script>

<Shell tab="historial">
	<div class="header"><h1>Historial</h1></div>

	{#if logs.length === 0}
		<p class="hint">Sin entrenamientos todavía.</p>
	{:else}
		{#each logs as log}
			<div class="log-card">
				<div class="log-header" onclick={() => toggle(log.id)}>
					<span class="chevron">{expanded.has(log.id) ? '▾' : '▸'}</span>
					<div class="log-meta">
						<span class="log-date">{fmtDate(log.date)}</span>
						<span class="log-routine">{log.routine_name}</span>
					</div>
					<span class="log-summary">
						{log.exercises.length} bl · {totalExs(log.exercises)} ej · {totalDuration(log.exercises)}
					</span>
					<button class="btn-del" onclick={(e) => remove(log.id, e)}>✕</button>
				</div>

				{#if expanded.has(log.id)}
					<div class="log-bloques">
						{#each log.exercises as bloque, bi}
							<div class="log-bloque">
								<p class="bloque-name">{bloque.name || `Bloque ${bi + 1}`}</p>
								{#each bloque.exercises as ex, ei}
									{#if !isDescanso(ex.name)}
										<div class="log-ex">
											<span class="log-ex-name">{ex.name}</span>
											<span class="log-ex-dur">{fmt(ex.duration_s)}</span>
											<input
												type="number"
												inputmode="numeric"
												placeholder="—"
												value={bloque.marks?.[ei] ?? ''}
												oninput={(e) => setMark(log, bi, ei, e.currentTarget.value)}
												onblur={() => saveMark(log)}
												onclick={(e) => e.stopPropagation()}
												class="mark-edit"
											/>
										</div>
									{/if}
								{/each}
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/each}
	{/if}
</Shell>

<style>
	.header { margin-bottom: 16px; }
	h1 { font-size: 1.4rem; font-weight: 700; }

	.log-card {
		background: #1a1a1a; border-radius: 10px;
		margin-bottom: 8px; overflow: hidden;
	}
	.log-header {
		display: flex; align-items: center; gap: 10px;
		padding: 14px 16px; cursor: pointer;
		transition: background 0.15s;
	}
	.log-header:hover { background: #1e1e1e; }
	.chevron { font-size: 0.75rem; color: #555; flex: none; }
	.log-meta { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
	.log-date    { font-size: 0.72rem; color: #555; font-weight: 700; letter-spacing: 0.5px; }
	.log-routine { font-size: 0.95rem; font-weight: 700; color: #ccc; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.log-summary { font-size: 0.72rem; color: #444; flex: none; }
	.btn-del {
		background: none; border: none; color: #333; cursor: pointer;
		font-size: 0.85rem; padding: 4px 6px; flex: none;
	}
	.btn-del:hover { color: #ef4444; }

	.log-bloques {
		padding: 0 16px 14px; display: flex; flex-direction: column; gap: 14px;
	}
	.log-bloque { display: flex; flex-direction: column; gap: 5px; }
	.bloque-name {
		font-size: 0.72rem; color: #555; text-transform: uppercase;
		letter-spacing: 0.8px; font-weight: 700; margin-bottom: 2px;
	}
	.log-ex {
		display: flex; align-items: center; gap: 8px; font-size: 0.85rem;
	}
	.log-ex-name { flex: 1; color: #aaa; }
	.log-ex-dur  { color: #444; font-size: 0.78rem; width: 40px; text-align: right; }
	.mark-edit {
		width: 52px; text-align: center; font-size: 0.95rem; font-weight: 700;
		padding: 4px 6px; border-radius: 6px; color: #4ade80;
		background: #0f0f0f; border: 1px solid #2a2a2a;
		-moz-appearance: textfield;
	}
	.mark-edit::-webkit-outer-spin-button,
	.mark-edit::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
	.mark-edit:focus { border-color: #4ade80; outline: none; }

	.hint { color: #333; text-align: center; padding: 40px 0; font-size: 0.9rem; }
</style>
