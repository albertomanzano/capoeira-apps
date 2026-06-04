<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { supabase } from '$lib/supabase';
	import Shell from '$lib/Shell.svelte';

	type ExData    = { name: string; duration_s: number };
	type BloqueData = { name: string; exercises: ExData[] };
	type RutinaData = { name: string; exercises: BloqueData[] };

	const CFG_KEY = 'capoeira_timer_config';
	const CFG_DEFAULTS = { exercises: 7, exerciseMin: 1, pauseSec: 30, rounds: 2, roundBreakSec: 60 };
	const CFG_LIMITS = {
		exercises:     { min: 1,  max: 12,  step: 1  },
		exerciseMin:   { min: 1,  max: 10,  step: 1  },
		pauseSec:      { min: 10, max: 120, step: 5  },
		rounds:        { min: 1,  max: 5,   step: 1  },
		roundBreakSec: { min: 0,  max: 300, step: 30 },
	};

	let cfg           = $state({ ...CFG_DEFAULTS });
	let routineBloque = $state<BloqueData | null>(null);
	let routineData   = $state<RutinaData | null>(null);
	let routineMeta   = $state<{ routine_id: string; routine_name: string } | null>(null);

	function loadCfg() {
		const raw = typeof localStorage !== 'undefined' && localStorage.getItem(CFG_KEY);
		if (raw) cfg = { ...CFG_DEFAULTS, ...JSON.parse(raw) };
	}
	function saveCfg() { localStorage.setItem(CFG_KEY, JSON.stringify(cfg)); }

	function adjustCfg(key: keyof typeof cfg, sign: number) {
		const { min, max, step } = CFG_LIMITS[key];
		cfg[key] = Math.max(min, Math.min(max, cfg[key] + sign * step));
		saveCfg();
		if (!running) rebuildAndReset();
	}

	const isDescanso = (name: string) => /^descanso$/i.test(name.trim());

	function buildPhasesFromExList(exList: { name: string; dur: number }[]) {
		const phases: { name: string; type: string; duration: number }[] = [];
		for (let i = 0; i < exList.length; i++) {
			const ex = exList[i];
			if (isDescanso(ex.name)) {
				phases.push({ name: 'Descanso', type: 'pausa', duration: ex.dur });
			} else {
				phases.push({ name: ex.name, type: 'ejercicio', duration: ex.dur });
				const nextIsDescanso = i < exList.length - 1 && isDescanso(exList[i + 1].name);
				if (i < exList.length - 1 && !nextIsDescanso) {
					phases.push({ name: 'Pausa', type: 'pausa', duration: cfg.pauseSec });
				}
			}
		}
		return phases;
	}

	function buildPhases() {
		if (routineData) {
			const phases: { name: string; type: string; duration: number; bloque?: string }[] = [];
			routineData.exercises.forEach((bloque) => {
				const exList = bloque.exercises.map(e => ({ name: e.name, dur: e.duration_s }));
				buildPhasesFromExList(exList).forEach(p => phases.push({ ...p, bloque: bloque.name }));
			});
			return phases;
		}
		const exList = routineBloque
			? routineBloque.exercises.map(e => ({ name: e.name, dur: e.duration_s }))
			: Array.from({ length: cfg.exercises }, (_, i) => ({ name: `Ejercicio ${i + 1}`, dur: cfg.exerciseMin * 60 }));
		return buildPhasesFromExList(exList);
	}

	let PHASES        = $state(buildPhases());
	let ROUNDS        = $derived(cfg.rounds);

	let round         = $state(0);
	let phase         = $state(0);
	let timeLeft      = $state(PHASES[0].duration);
	let running       = $state(false);
	let finished      = $state(false);
	let inRoundBreak  = $state(false);
	let started       = $state(false);

	// marks state
	let marks        = $state<(number | null)[]>([]);
	let currentExIdx = $state(0);
	let lastExName   = $state('');
	let logSaved     = $state(false);
	let logBusy      = $state(false);

	let voices        = $state<SpeechSynthesisVoice[]>([]);
	let selectedVoice = $state<SpeechSynthesisVoice | null>(null);

	let audioCtx: AudioContext | null = null;
	let ticker: ReturnType<typeof setInterval> | null = null;

	const curDuration = $derived(inRoundBreak ? cfg.roundBreakSec : PHASES[phase].duration);
	const elapsed     = $derived(curDuration - timeLeft);
	const pct         = $derived(Math.max(0, (elapsed / curDuration) * 100));
	const isPausa     = $derived(!inRoundBreak && PHASES[phase].type === 'pausa');
	const timerText   = $derived(`${Math.floor(elapsed / 60)}:${(elapsed % 60).toString().padStart(2, '0')}`);
	const nextPhase   = $derived(PHASES[phase + 1]);
	const nextIsRound = $derived(phase + 1 >= PHASES.length);
	const isLast      = $derived(nextIsRound && round >= ROUNDS - 1);
	const nextInfo    = $derived(
		finished       ? '' :
		inRoundBreak   ? `A continuación: Bloque ${round + 2}` :
		isLast         ? 'Último ejercicio' :
		nextIsRound    ? (cfg.roundBreakSec > 0 ? 'A continuación: Descanso' : `A continuación: Bloque ${round + 2}`) :
		nextPhase?.type === 'pausa' ? 'A continuación: Pausa' :
		`A continuación: ${nextPhase?.name}`
	);

	const hasRoutine     = $derived(!!(routineBloque || routineData));
	const showMarkInput  = $derived(
		hasRoutine && started && !finished && marks.length > 0 && currentExIdx < marks.length
	);

	function initMarks() {
		const total = PHASES.filter(p => p.type === 'ejercicio').length;
		marks = Array(total).fill(null);
		currentExIdx = 0;
		lastExName = PHASES[0]?.type === 'ejercicio' ? PHASES[0].name : '';
		logSaved = false;
	}

	function getCtx(): AudioContext {
		if (!audioCtx) audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
		return audioCtx;
	}

	function tone(freq: number, dur: number, vol = 0.4, delay = 0) {
		const c = getCtx();
		const osc = c.createOscillator(); const gain = c.createGain();
		osc.connect(gain); gain.connect(c.destination);
		osc.frequency.value = freq;
		const t = c.currentTime + delay;
		gain.gain.setValueAtTime(vol, t);
		gain.gain.exponentialRampToValueAtTime(0.001, t + dur);
		osc.start(t); osc.stop(t + dur + 0.05);
	}

	function beepWarning()    { tone(660, 0.08, 0.25); }
	function beepTransition() { tone(880,0.08,0.4,0); tone(880,0.08,0.4,0.15); tone(880,0.08,0.4,0.30); tone(1320,0.35,0.5,0.50); }
	function beepEndRound()   { tone(880,0.12,0.5,0); tone(880,0.12,0.5,0.18); tone(1320,0.35,0.6,0.36); tone(1320,0.45,0.6,0.90); }

	function speak(text: string) {
		if (!window.speechSynthesis) return;
		window.speechSynthesis.cancel();
		const utt = new SpeechSynthesisUtterance(text);
		utt.lang = 'es-ES'; utt.rate = 0.88; utt.pitch = 1.0;
		if (selectedVoice) utt.voice = selectedVoice;
		window.speechSynthesis.speak(utt);
	}

	function populateVoices() {
		const v = window.speechSynthesis.getVoices();
		if (!v.length) return;
		voices = v;
		const saved = localStorage.getItem('capoeira_voice');
		const match = saved ? v.find(x => x.name === saved) : null;
		if (match) { selectedVoice = match; return; }
		const spanish = v.filter(x => x.lang.startsWith('es'));
		const premium = spanish.find(x => /natural|neural|premium|enhanced/i.test(x.name));
		selectedVoice = premium || spanish[0] || v[0] || null;
	}

	function selectVoice(i: number) {
		selectedVoice = voices[i];
		if (selectedVoice) localStorage.setItem('capoeira_voice', selectedVoice.name);
	}

	function startNextRound() {
		currentExIdx = 0;
		lastExName = PHASES[0]?.name ?? '';
		beepTransition();
		speak(`Bloque ${round + 1}. ${PHASES[0].name}`);
		timeLeft = PHASES[0].duration;
	}

	function endRoundBreak() {
		inRoundBreak = false;
		round++;
		phase = 0;
		startNextRound();
	}

	function advance() {
		phase++;
		if (phase >= PHASES.length) {
			if (round + 1 >= ROUNDS) { phase = 0; doFinish(); return; }
			phase = 0;
			if (cfg.roundBreakSec > 0) {
				inRoundBreak = true;
				timeLeft = cfg.roundBreakSec;
				beepEndRound();
				speak('Descansando');
				return;
			}
			round++;
			startNextRound();
			return;
		}
		beepTransition();
		const p = PHASES[phase];
		speak(p.type === 'pausa' ? 'Pausa' : p.name);
		timeLeft = p.duration;
		if (p.type === 'ejercicio') {
			currentExIdx++;
			lastExName = p.name;
		}
	}

	function doFinish() {
		if (ticker) { clearInterval(ticker); ticker = null; }
		running = false; finished = true; beepEndRound();
	}

	function rebuildAndReset() {
		if (ticker) { clearInterval(ticker); ticker = null; }
		PHASES = buildPhases();
		running = false; finished = false; started = false; inRoundBreak = false;
		round = 0; phase = 0; timeLeft = PHASES[0].duration;
		marks = []; currentExIdx = 0; lastExName = ''; logSaved = false; logBusy = false;
	}

	function startStop() {
		getCtx();
		if (running) {
			if (ticker) { clearInterval(ticker); ticker = null; }
			running = false;
		} else {
			if (!started) {
				started = true;
				if (hasRoutine) initMarks();
				beepTransition();
				speak(PHASES[0].name);
			}
			ticker = setInterval(() => {
				timeLeft--;
				if (inRoundBreak) {
					if (timeLeft === 3 || timeLeft === 2 || timeLeft === 1) beepWarning();
					else if (timeLeft >= 4 && timeLeft <= 10) speak(String(timeLeft));
					if (timeLeft <= 0) endRoundBreak();
					return;
				}
				const e = PHASES[phase].duration - timeLeft;
				const isPausaPhase = PHASES[phase].type === 'pausa';
				if (timeLeft === 3 || timeLeft === 2 || timeLeft === 1) beepWarning();
				else if (isPausaPhase && timeLeft >= 4 && timeLeft <= 10) speak(String(timeLeft));
				else if (!isPausaPhase && e > 0 && e % 5 === 0) speak(String(e));
				if (timeLeft <= 0) advance();
			}, 1000);
			running = true;
		}
	}

	async function saveLog() {
		if (!routineMeta) return;
		logBusy = true;
		const { data: { user } } = await supabase.auth.getUser();
		if (!user) { logBusy = false; return; }

		let bloques: { name: string; exercises: ExData[]; marks: (number | null)[] }[];
		let mIdx = 0;

		if (routineData) {
			bloques = routineData.exercises.map(bloque => {
				const exs = bloque.exercises.filter(e => !isDescanso(e.name));
				const bMarks = exs.map(() => marks[mIdx++] ?? null);
				return { name: bloque.name, exercises: exs, marks: bMarks };
			});
		} else if (routineBloque) {
			const exs = routineBloque.exercises.filter(e => !isDescanso(e.name));
			const bMarks = exs.map(() => marks[mIdx++] ?? null);
			bloques = [{ name: routineBloque.name, exercises: exs, marks: bMarks }];
		} else {
			logBusy = false;
			return;
		}

		await supabase.from('training_logs').insert({
			user_id:      user.id,
			routine_id:   routineMeta.routine_id,
			routine_name: routineMeta.routine_name,
			exercises:    bloques,
			marks:        [],
			date:         new Date().toISOString().split('T')[0],
		});
		logSaved = true;
		logBusy = false;
	}

	onMount(() => {
		loadCfg();
		const rawRutina = localStorage.getItem('capoeira_timer_rutina');
		const rawBloque = localStorage.getItem('capoeira_timer_bloque');
		const rawMeta   = localStorage.getItem('capoeira_timer_meta');
		if (rawRutina) {
			routineData = JSON.parse(rawRutina);
			localStorage.removeItem('capoeira_timer_rutina');
		} else if (rawBloque) {
			routineBloque = JSON.parse(rawBloque);
			localStorage.removeItem('capoeira_timer_bloque');
		}
		if (rawMeta) {
			routineMeta = JSON.parse(rawMeta);
			localStorage.removeItem('capoeira_timer_meta');
		}
		PHASES = buildPhases();
		timeLeft = PHASES[0].duration;
		if (window.speechSynthesis) {
			window.speechSynthesis.onvoiceschanged = populateVoices;
			populateVoices();
		}
	});

	onDestroy(() => {
		if (ticker) clearInterval(ticker);
		if (typeof window !== 'undefined') window.speechSynthesis?.cancel();
	});
</script>

<Shell tab="timer">
	{#if routineData}
		<p class="routine-pill">▶ {routineData.name}</p>
	{:else if routineBloque}
		<p class="routine-pill">{routineBloque.name || 'Bloque'}</p>
	{/if}

	{#if !finished}
		<div class="timer-wrap">
			{#if inRoundBreak}
				<p class="round-info">Descanso entre bloques</p>
				<p class="phase-label round-break">Bloque {round + 1} → {round + 2}</p>
				<p class="phase-name"></p>
			{:else}
				<p class="round-info">
					{#if routineData && PHASES[phase]?.bloque}
						{PHASES[phase].bloque}
					{:else}
						Bloque {round + 1} de {ROUNDS}
					{/if}
				</p>
				<p class="phase-label {isPausa ? 'pausa' : ''}">{isPausa ? 'Pausa' : 'Ejercicio'}</p>
				<p class="phase-name">{isPausa ? '' : PHASES[phase].name}</p>
			{/if}

			<p class="timer {isPausa ? 'pausa' : ''} {inRoundBreak ? 'round-break' : ''} {!isPausa && !inRoundBreak && timeLeft <= 5 ? 'warning' : ''}">
				{timerText}
			</p>

			<div class="bar-wrap">
				<div class="bar {isPausa ? 'pausa' : ''} {inRoundBreak ? 'round-break' : ''} {!isPausa && !inRoundBreak && timeLeft <= 5 ? 'warning' : ''}"
					style="width: {pct}%"></div>
			</div>

			{#if showMarkInput}
				<div class="mark-row">
					<span class="mark-ex-name">{lastExName}</span>
					<input
						type="number"
						inputmode="numeric"
						placeholder="reps"
						value={marks[currentExIdx] ?? ''}
						oninput={(e) => { marks[currentExIdx] = e.currentTarget.value ? Number(e.currentTarget.value) : null; }}
						class="mark-input-timer"
					/>
				</div>
			{/if}

			{#if routineData}
				<div class="dots-rutina">
					{#each routineData.exercises as bloque}
						{@const bloquePhases = PHASES.map((p, i) => ({ ...p, i })).filter(p => p.bloque === bloque.name)}
						<div class="dots-row">
							{#if bloque.name}<span class="dots-label">{bloque.name}</span>{/if}
							<div class="dots">
								{#each bloquePhases as p}
									<div class="dot {p.type === 'pausa' ? 'is-pausa' : ''} {p.i < phase ? 'done' : ''} {p.i === phase && !inRoundBreak ? 'current' : ''}"></div>
								{/each}
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="dots">
					{#each PHASES as p, i}
						<div class="dot {p.type === 'pausa' ? 'is-pausa' : ''} {i < phase ? 'done' : ''} {i === phase && !inRoundBreak ? 'current' : ''}"></div>
					{/each}
				</div>
			{/if}

			<p class="next-info">{nextInfo}</p>

			<div class="controls">
				<button class="btn-start {running ? 'running' : ''}" onclick={startStop}>
					{running ? 'Pausar' : started ? 'Continuar' : 'Empezar'}
				</button>
				<button class="btn-reset" onclick={rebuildAndReset}>Reset</button>
			</div>
		</div>
	{:else}
		<div class="finished">
			<p class="finished-title">¡Completado!</p>
			<p class="finished-sub">{ROUNDS} bloque{ROUNDS !== 1 ? 's' : ''} terminado{ROUNDS !== 1 ? 's' : ''}</p>
			{#if routineMeta && !logSaved}
				<button class="btn-save-log" onclick={saveLog} disabled={logBusy}>
					{logBusy ? 'Guardando…' : 'Guardar entreno'}
				</button>
			{:else if logSaved}
				<p class="log-saved">✓ Guardado en historial</p>
			{/if}
			<button class="btn-start" onclick={rebuildAndReset}>Volver a empezar</button>
		</div>
	{/if}

	<details class="config-settings" class:disabled={running}>
		<summary>Configurar</summary>
		<div class="config-panel">
			{#each [
				{ key: 'exercises',     label: 'Ejercicios',           hide: !!routineBloque },
				{ key: 'exerciseMin',   label: 'Min / ejercicio',      hide: !!routineBloque },
				{ key: 'pauseSec',      label: 'Pausa (s)',            hide: false },
				{ key: 'rounds',        label: 'Bloques',              hide: false },
				{ key: 'roundBreakSec', label: 'Descanso bloques (s)', hide: false },
			] as row}
				{#if !row.hide}
					<div class="cfg-row">
						<span class="cfg-label">{row.label}</span>
						<div class="stepper">
							<button onclick={() => adjustCfg(row.key as keyof typeof cfg, -1)} disabled={running}>−</button>
							<span>{cfg[row.key as keyof typeof cfg]}</span>
							<button onclick={() => adjustCfg(row.key as keyof typeof cfg, 1)} disabled={running}>+</button>
						</div>
					</div>
				{/if}
			{/each}
			{#if running}<p class="cfg-note">Para cambiar: pausar y hacer reset</p>{/if}
		</div>
	</details>

	<details class="voice-settings">
		<summary>Voz</summary>
		<div class="voice-panel">
			<select class="voice-select"
				value={voices.indexOf(selectedVoice!)}
				onchange={(e) => selectVoice(parseInt(e.currentTarget.value))}>
				{#each voices as v, i}
					<option value={i}>{v.name} ({v.lang})</option>
				{/each}
			</select>
			<button class="btn-test" onclick={() => speak('Ejercicio uno. Diez. Veinte. Treinta.')}>Probar</button>
		</div>
	</details>
</Shell>

<style>
	.routine-pill {
		text-align: center; font-size: 0.78rem; color: #4ade80;
		background: #0d1f0d; border: 1px solid #1a3a1a; border-radius: 20px;
		padding: 4px 14px; margin: 0 auto 12px; width: fit-content;
	}
	.timer-wrap {
		display: flex; flex-direction: column; align-items: center;
		padding-top: 12px; text-align: center;
	}
	.round-info   { font-size: 0.95rem; color: #555; letter-spacing: 1px; margin-bottom: 4px; }
	.phase-label  { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 3px; color: #888; margin-bottom: 4px; }
	.phase-label.pausa       { color: #4ecdc4; }
	.phase-label.round-break { color: #f59e0b; }
	.phase-name   { font-size: 1.8rem; font-weight: 700; min-height: 2.2rem; margin-bottom: 20px; }
	.timer { font-size: 7rem; font-weight: 800; font-variant-numeric: tabular-nums; line-height: 1; margin-bottom: 10px; }
	.timer.pausa       { color: #4ecdc4; }
	.timer.round-break { color: #f59e0b; }
	.timer.warning     { color: #ff6b35; }
	.bar-wrap { width: 100%; max-width: 340px; height: 5px; background: #222; border-radius: 3px; margin-bottom: 16px; overflow: hidden; }
	.bar { height: 100%; border-radius: 3px; background: #4ade80; transition: width 0.9s linear, background 0.3s; }
	.bar.pausa       { background: #4ecdc4; }
	.bar.round-break { background: #f59e0b; }
	.bar.warning     { background: #ff6b35; }

	.mark-row {
		display: flex; align-items: center; justify-content: space-between;
		gap: 12px; margin-bottom: 16px;
		background: #1a1a1a; border-radius: 10px; padding: 10px 16px;
		width: 100%; max-width: 340px;
	}
	.mark-ex-name { font-size: 0.85rem; color: #888; flex: 1; text-align: left; }
	.mark-input-timer {
		width: 80px; flex: none; text-align: center;
		font-size: 1.3rem; font-weight: 700;
		padding: 8px; border-radius: 8px;
		background: #0f0f0f; border: 1px solid #333; color: #fff;
	}

	.dots-rutina { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; width: 100%; }
	.dots-row { display: flex; align-items: center; gap: 8px; }
	.dots-label { font-size: 0.65rem; color: #444; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap; width: 80px; text-align: right; flex: none; }
	.dots { display: flex; align-items: center; gap: 5px; flex-wrap: wrap; }
	.dot { width: 10px; height: 10px; border-radius: 50%; background: #2a2a2a; transition: background 0.3s; }
	.dot.done    { background: #4ade80; }
	.dot.current { background: #fff; }
	.dot.is-pausa { width: 5px; height: 5px; }
	.dot.is-pausa.done    { background: #2a6b67; }
	.dot.is-pausa.current { background: #4ecdc4; }
	.next-info { font-size: 0.9rem; color: #444; margin-bottom: 32px; min-height: 1.1rem; }
	.controls  { display: flex; gap: 14px; }
	.btn-start { padding: 18px 36px; font-size: 1.15rem; font-weight: 700; border: none; border-radius: 14px; cursor: pointer; min-width: 150px; background: #4ade80; color: #0f0f0f; }
	.btn-start.running { background: #facc15; }
	.btn-start:active { transform: scale(0.97); }
	.btn-reset { padding: 18px 24px; font-size: 1.15rem; font-weight: 700; border: none; border-radius: 14px; cursor: pointer; background: #1e1e1e; color: #aaa; }
	.btn-reset:active { transform: scale(0.97); }
	.finished { display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; padding-top: 40px; }
	.finished-title { font-size: 2.2rem; color: #4ade80; font-weight: 700; }
	.finished-sub   { color: #666; }
	.btn-save-log {
		padding: 14px 28px; font-size: 1rem; font-weight: 700;
		border: 1px solid #2a4a2a; border-radius: 12px; cursor: pointer;
		background: #1a1a1a; color: #4ade80;
		width: 100%; max-width: 260px;
	}
	.btn-save-log:disabled { opacity: 0.5; cursor: default; }
	.log-saved { color: #4ade80; font-size: 0.9rem; }

	.config-settings, .voice-settings { margin-top: 24px; font-size: 0.85rem; color: #444; }
	.config-settings summary, .voice-settings summary { cursor: pointer; user-select: none; }
	.config-panel, .voice-panel {
		display: flex; flex-direction: column; gap: 8px;
		margin-top: 8px; background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 10px 12px;
	}
	.cfg-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
	.cfg-label { font-size: 0.8rem; color: #777; }
	.stepper { display: flex; align-items: center; gap: 6px; }
	.stepper button {
		width: 28px; height: 28px; padding: 0;
		background: #2a2a2a; color: #aaa; border: 1px solid #333;
		border-radius: 6px; font-size: 1.1rem; cursor: pointer;
		display: flex; align-items: center; justify-content: center;
	}
	.stepper button:disabled { opacity: 0.3; cursor: default; }
	.stepper span { color: #ccc; font-size: 0.9rem; min-width: 28px; text-align: center; }
	.cfg-note { font-size: 0.75rem; color: #555; text-align: center; }

	.voice-select { background: #222; color: #ccc; border: 1px solid #444; border-radius: 6px; padding: 6px 8px; font-size: 0.8rem; }
	.btn-test { padding: 6px 12px; font-size: 0.8rem; background: #333; color: #aaa; border: none; border-radius: 6px; cursor: pointer; align-self: flex-start; }
</style>
