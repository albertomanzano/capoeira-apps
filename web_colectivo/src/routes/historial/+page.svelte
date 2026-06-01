<script lang="ts">
	import { supabase } from '$lib/supabase';
	import Shell from '$lib/Shell.svelte';

	type Ex  = { name: string; duration_s: number };
	type Log = {
		id: string; date: string; routine_name: string;
		exercises: Ex[]; marks: (number | null)[];
	};

	let logs = $state<Log[]>([]);

	function fmt(s: number): string {
		if (s < 60) return `${s}s`;
		const m = Math.floor(s / 60), r = s % 60;
		return r ? `${m}m${r}s` : `${m}m`;
	}

	function fmtDate(d: string): string {
		const [y, m, day] = d.split('-');
		return `${day}/${m}/${y.slice(2)}`;
	}

	async function load() {
		const { data } = await supabase
			.from('training_logs')
			.select('id, date, routine_name, exercises, marks')
			.order('date', { ascending: false })
			.limit(60);
		logs = (data ?? []) as Log[];
	}

	async function remove(id: string) {
		if (!confirm('¿Borrar esta entrada?')) return;
		await supabase.from('training_logs').delete().eq('id', id);
		await load();
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
				<div class="log-header">
					<div class="log-meta">
						<span class="log-date">{fmtDate(log.date)}</span>
						<span class="log-routine">{log.routine_name}</span>
					</div>
					<button class="btn-del" onclick={() => remove(log.id)}>✕</button>
				</div>
				<div class="log-exs">
					{#each log.exercises as ex, i}
						<div class="log-ex">
							<span class="log-ex-name">{ex.name}</span>
							<span class="log-ex-dur">{fmt(ex.duration_s)}</span>
							<span class="log-mark">{log.marks[i] ?? '—'}</span>
						</div>
					{/each}
				</div>
			</div>
		{/each}
	{/if}
</Shell>

<style>
	.header { margin-bottom: 16px; }
	h1 { font-size: 1.4rem; font-weight: 700; }

	.log-card {
		background: #1a1a1a; border-radius: 10px;
		padding: 14px 16px; margin-bottom: 10px;
	}
	.log-header {
		display: flex; align-items: flex-start; justify-content: space-between;
		margin-bottom: 10px;
	}
	.log-meta { display: flex; flex-direction: column; gap: 3px; }
	.log-date    { font-size: 0.72rem; color: #555; font-weight: 700; letter-spacing: 0.5px; }
	.log-routine { font-size: 0.95rem; font-weight: 700; color: #ccc; }
	.btn-del {
		background: none; border: none; color: #333; cursor: pointer;
		font-size: 0.85rem; padding: 2px 6px;
	}
	.btn-del:hover { color: #ef4444; }

	.log-exs { display: flex; flex-direction: column; gap: 6px; }
	.log-ex {
		display: flex; align-items: center; gap: 8px;
		font-size: 0.85rem;
	}
	.log-ex-name { flex: 1; color: #aaa; }
	.log-ex-dur  { color: #444; font-size: 0.78rem; width: 40px; text-align: right; }
	.log-mark    { color: #4ade80; font-weight: 700; width: 36px; text-align: right; }

	.hint { color: #333; text-align: center; padding: 40px 0; font-size: 0.9rem; }
</style>
