<script lang="ts">
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import Shell from '$lib/Shell.svelte';

	type Ex        = { name: string; duration_s: number };
	type BloqueLog = { name: string; exercises: Ex[]; marks: (number | null)[] };
	type Log = { id: string; date: string; routine_name: string; exercises: BloqueLog[] };
	type Group = { name: string; lastDate: string; logs: Log[] };

	let logs           = $state<Log[]>([]);
	let expandedGroups = $state<Set<string>>(new Set());

	function computeGroups(ls: Log[]): Group[] {
		const map = new Map<string, Log[]>();
		for (const log of ls) {
			if (!map.has(log.routine_name)) map.set(log.routine_name, []);
			map.get(log.routine_name)!.push(log);
		}
		return Array.from(map.entries())
			.map(([name, grpLogs]) => ({ name, lastDate: grpLogs[0].date, logs: grpLogs }))
			.sort((a, b) => b.lastDate.localeCompare(a.lastDate));
	}

	let groups = $derived(computeGroups(logs));

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

	function toggleGroup(name: string) {
		const s = new Set(expandedGroups);
		if (s.has(name)) s.delete(name); else s.add(name);
		expandedGroups = s;
	}

	async function remove(id: string, e: MouseEvent) {
		e.stopPropagation();
		if (!confirm('¿Borrar esta entrada?')) return;
		await supabase.from('training_logs').delete().eq('id', id);
		await load();
	}

	$effect(() => { load(); });
</script>

<Shell tab="historial">
	<div class="header">
		<h1>Historial</h1>
		<button class="btn-add" onclick={() => goto('/members/historial/nueva')}>+ Añadir</button>
	</div>

	{#if groups.length === 0}
		<p class="hint">Sin entrenamientos todavía.</p>
	{:else}
		{#each groups as group}
			<div class="group-card">
				<div class="group-header" onclick={() => toggleGroup(group.name)}>
					<span class="chevron">{expandedGroups.has(group.name) ? '▾' : '▸'}</span>
					<div class="group-meta">
						<span class="group-name">{group.name}</span>
						<span class="group-sub">
							{group.logs.length} {group.logs.length === 1 ? 'sesión' : 'sesiones'} · última {fmtDate(group.lastDate)}
						</span>
					</div>
				</div>

				{#if expandedGroups.has(group.name)}
					<div class="group-entries">
						{#each group.logs as log}
							<div class="entry-row" onclick={() => goto(`/members/historial/${log.id}`)}>
								<span class="log-date">{fmtDate(log.date)}</span>
								<span class="log-summary">{log.exercises.length} bl · {totalExs(log.exercises)} ej · {totalDuration(log.exercises)}</span>
								<button class="btn-del" onclick={(e) => remove(log.id, e)}>✕</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/each}
	{/if}
</Shell>

<style>
	.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
	h1 { font-size: 1.4rem; font-weight: 700; }
	.btn-add {
		background: var(--accent); color: var(--accent-on); border: none; border-radius: 8px;
		padding: 8px 14px; font-size: 0.85rem; font-weight: 700; cursor: pointer;
	}

	.group-card {
		background: var(--surface); border-radius: 10px;
		margin-bottom: 8px; overflow: hidden;
	}
	.group-header {
		display: flex; align-items: center; gap: 10px;
		padding: 14px 16px; cursor: pointer;
		transition: background 0.15s;
	}
	.group-header:hover { background: var(--surface-hover); }
	.chevron { font-size: 0.75rem; color: #555; flex: none; }
	.group-meta { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
	.group-name {
		font-size: 0.95rem; font-weight: 700; color: var(--text);
		overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
	}
	.group-sub { font-size: 0.72rem; color: #555; }

	.group-entries { border-top: 1px solid var(--border); }
	.entry-row {
		display: flex; align-items: center; gap: 10px;
		padding: 11px 16px 11px 28px; cursor: pointer;
		border-bottom: 1px solid var(--border); transition: background 0.15s;
	}
	.entry-row:last-child { border-bottom: none; }
	.entry-row:hover { background: var(--surface-hover); }
	.log-date { font-size: 0.85rem; font-weight: 700; color: #888; flex: none; }
	.log-summary { font-size: 0.72rem; color: #444; flex: 1; }
	.btn-del {
		background: none; border: none; color: #333; cursor: pointer;
		font-size: 0.85rem; padding: 4px 6px; flex: none;
	}
	.btn-del:hover { color: #ef4444; }

	.hint { color: #333; text-align: center; padding: 40px 0; font-size: 0.9rem; }
</style>
