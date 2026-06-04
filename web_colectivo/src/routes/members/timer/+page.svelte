<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { supabase } from '$lib/supabase';
	import Shell from '$lib/Shell.svelte';

	type ExData     = { name: string; duration_s: number };
	type BloqueData = { name: string; exercises: ExData[] };
	type RutinaData = { name: string; exercises: BloqueData[] };
	type BloqueLog  = { name: string; exercises: ExData[]; marks: (number | null)[] };

	const CFG_KEY = 'capoeira_timer_config';
	const CFG_DEFAULTS = { pauseSec: 30, rounds: 2, roundBreakSec: 60 };
	const CFG_LIMITS = {
		pauseSec:      { min: 10, max: 120, step: 5  },
		rounds:        { min: 1,  max: 5,   step: 1  },
		roundBreakSec: { min: 0,  max: 300, step: 30 },
	};

	let cfg           = $state({ ...CFG_DEFAULTS });
	let routineBloque = $state<BloqueData | null>(null);
	let routineData   = $state<RutinaData | null>(null);
	let routineMeta   = $state<{ routine_id: string; routine_name: string } | null>(null);
	let mounted       = $state(false);

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
		if (routineBloque) {
			return buildPhasesFromExList(routineBloque.exercises.map(e => ({ name: e.name, dur: e.duration_s })));
		}
		return [{ name: '', type: 'ejercicio', duration: 60 }];
	}

	let PHASES       = $state(buildPhases());
	// rutina completa: sus bloques ya están en secuencia, se ejecuta una sola vez
	let ROUNDS       = $derived(routineData ? 1 : cfg.rounds);
	let noRoutine    = $derived(mounted && !routineData && !routineBloque);

	let round        = $state(0);
	let phase        = $state(0);
	let timeLeft     = $state(PHASES[0].duration);
	let running      = $state(false);
	let finished     = $state(false);
	let inRoundBreak = $state(false);
	let started      = $state(false);

	let marks        = $state<(number | null)[]>([]);
	let lastMarks    = $state<(number | null)[]>([]);
	let currentExIdx = $state(0);
	let lastExName   = $state('');
	let logSaved     = $state(false);
	let logBusy      = $state(false);

	let selectedVoice = $state<SpeechSynthesisVoice | null>(null);

	let audioCtx: AudioContext | null = null;
	let ticker: ReturnType<typeof setInterval> | null = null;

	const curDuration    = $derived(inRoundBreak ? cfg.roundBreakSec : PHASES[phase].duration);
	const elapsed        = $derived(curDuration - timeLeft);
	const pct            = $derived(Math.max(0, (elapsed / curDuration) * 100));
	const isPausa        = $derived(!inRoundBreak && PHASES[phase].type === 'pausa');
	const timerText      = $derived(`${Math.floor(elapsed / 60)}:${(elapsed % 60).toString().padStart(2, '0')}`);
	const nextPhase      = $derived(PHASES[phase + 1]);
	const nextIsRound    = $derived(phase + 1 >= PHASES.length);
	const isLast         = $derived(nextIsRound && round >= ROUNDS - 1);
	const nextInfo       = $derived(
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
		const saved = localStorage.getItem('capoeira_voice');
		const match = saved ? v.find(x => x.name === saved) : null;
		if (match) { selectedVoice = match; return; }
		const spanish = v.filter(x => x.lang.startsWith('es'));
		const premium = spanish.find(x => /natural|neural|premium|enhanced/i.test(x.name));
		selectedVoice = premium || spanish[0] || v[0] || null;
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

	async function loadLastMarks() {
		if (!routineMeta?.routine_id) return;
		const { data } = await supabase
			.from('training_logs')
			.select('exercises')
			.eq('routine_id', routineMeta.routine_id)
			.order('date', { ascending: false })
			.limit(1)
			.single();
		if (!data) return;

		const logBloques: BloqueLog[] = data.exercises ?? [];
		const flat: (number | null)[] = [];

		if (routineData) {
			for (const bloque of logBloques) {
				const exs = bloque.exercises ?? [];
				exs.forEach((e, i) => {
					if (!isDescanso(e.name)) flat.push(bloque.marks?.[i] ?? null);
				});
			}
		} else if (routineBloque) {
			const match = logBloques.find(b => b.name === routineBloque!.name) ?? logBloques[0];
			if (match) {
				(match.exercises ?? []).forEach((e, i) => {
					if (!isDescanso(e.name)) flat.push(match.marks?.[i] ?? null);
				});
			}
		}
		lastMarks = flat;
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
		loadLastMarks();
		timeLeft = PHASES[0].duration;
		mounted = true;
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
	{#if noRoutine}
		<div class="no-routine">
			<p class="no-routine-text">Lanza el entrenamiento desde una rutina.</p>
			<a href="/members/rutinas" class="btn-go">Ver rutinas</a>
		</div>

	{:else}
		{#if !finished}
			<div class="timer-wrap">
				{#if inRoundBreak}
					<p class="phase-name">Descanso</p>
				{:else}
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
					<input
						type="number"
						inputmode="numeric"
						placeholder="—"
						value={marks[currentExIdx] ?? ''}
						oninput={(e) => { marks[currentExIdx] = e.currentTarget.value ? Number(e.currentTarget.value) : null; }}
						class="mark-input-timer"
					/>
					{#if lastMarks[currentExIdx] != null}
						<p class="last-mark">Última vez: {lastMarks[currentExIdx]}</p>
					{/if}
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

	{/if}
</Shell>

<style>
	.no-routine {
		display: flex; flex-direction: column; align-items: center;
		gap: 20px; padding-top: 80px; text-align: center;
	}
	.no-routine-text { color: #555; font-size: 1rem; }
	.btn-go {
		padding: 12px 24px; background: #4ade80; color: #0f0f0f;
		border-radius: 10px; font-weight: 700; text-decoration: none; font-size: 0.95rem;
	}

.timer-wrap {
		display: flex; flex-direction: column; align-items: center;
		padding-top: 12px; text-align: center;
	}
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

	.mark-input-timer {
		width: 120px; text-align: center; margin-bottom: 16px;
		font-size: 2rem; font-weight: 700;
		padding: 10px; border-radius: 10px;
		background: #1a1a1a; border: 1px solid #333; color: #fff;
		-moz-appearance: textfield;
	}
	.mark-input-timer::-webkit-outer-spin-button,
	.mark-input-timer::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
	.last-mark { font-size: 0.8rem; color: #555; margin-top: 4px; margin-bottom: 8px; }

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
	.btn-save-log {
		padding: 14px 28px; font-size: 1rem; font-weight: 700;
		border: 1px solid #2a4a2a; border-radius: 12px; cursor: pointer;
		background: #1a1a1a; color: #4ade80;
		width: 100%; max-width: 260px;
	}
	.btn-save-log:disabled { opacity: 0.5; cursor: default; }
	.log-saved { color: #4ade80; font-size: 0.9rem; }

</style>
