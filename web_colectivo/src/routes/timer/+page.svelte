<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Shell from '$lib/Shell.svelte';

	const CFG_KEY = 'capoeira_timer_config';
	const CFG_DEFAULTS = { exercises: 7, exerciseMin: 1, pauseSec: 30, rounds: 2, roundBreakSec: 60 };
	const CFG_LIMITS = {
		exercises:     { min: 1,  max: 12,  step: 1  },
		exerciseMin:   { min: 1,  max: 10,  step: 1  },
		pauseSec:      { min: 10, max: 120, step: 5  },
		rounds:        { min: 1,  max: 5,   step: 1  },
		roundBreakSec: { min: 0,  max: 300, step: 30 },
	};

	let cfg = $state({ ...CFG_DEFAULTS });

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

	function buildPhases() {
		const dur = cfg.exerciseMin * 60;
		const phases: { name: string; type: string; duration: number }[] = [];
		for (let i = 0; i < cfg.exercises; i++) {
			phases.push({ name: `Ejercicio ${i + 1}`, type: 'ejercicio', duration: dur });
			if (i < cfg.exercises - 1) phases.push({ name: 'Pausa', type: 'pausa', duration: cfg.pauseSec });
		}
		return phases;
	}

	let PHASES        = $state(buildPhases());
	let ROUNDS        = $derived(cfg.rounds);

	let round         = $state(0);
	let phase         = $state(0);
	let timeLeft      = $state(PHASES[0].duration);
	let running       = $state(false);
	let finished      = $state(false);
	let inRoundBreak  = $state(false);
	let started       = false;

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
		inRoundBreak   ? `A continuación: Ronda ${round + 2}` :
		isLast         ? 'Último ejercicio' :
		nextIsRound    ? (cfg.roundBreakSec > 0 ? 'A continuación: Descanso' : `A continuación: Ronda ${round + 2}`) :
		nextPhase?.type === 'pausa' ? 'A continuación: Pausa' :
		`A continuación: ${nextPhase?.name}`
	);

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
		beepTransition();
		speak(`Ronda ${round + 1}. ${PHASES[0].name}`);
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
	}

	function startStop() {
		getCtx();
		if (running) {
			if (ticker) { clearInterval(ticker); ticker = null; }
			running = false;
		} else {
			if (!started) { started = true; beepTransition(); speak(PHASES[0].name); }
			ticker = setInterval(() => {
				timeLeft--;
				if (inRoundBreak) {
					if (timeLeft === 3 || timeLeft === 2 || timeLeft === 1) beepWarning();
					if (timeLeft <= 0) endRoundBreak();
					return;
				}
				const e = PHASES[phase].duration - timeLeft;
				if (timeLeft === 3 || timeLeft === 2 || timeLeft === 1) beepWarning();
				else if (e > 0 && e % 5 === 0) speak(String(e));
				if (timeLeft <= 0) advance();
			}, 1000);
			running = true;
		}
	}

	onMount(() => {
		loadCfg();
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
	{#if !finished}
		<div class="timer-wrap">
			{#if inRoundBreak}
				<p class="round-info">Descanso entre rondas</p>
				<p class="phase-label round-break">Ronda {round + 1} → {round + 2}</p>
				<p class="phase-name"></p>
			{:else}
				<p class="round-info">Ronda {round + 1} de {ROUNDS}</p>
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

			<div class="dots">
				{#each PHASES as p, i}
					<div class="dot {p.type === 'pausa' ? 'is-pausa' : ''} {i < phase ? 'done' : ''} {i === phase && !inRoundBreak ? 'current' : ''}"></div>
				{/each}
			</div>

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
			<p class="finished-sub">{ROUNDS} ronda{ROUNDS !== 1 ? 's' : ''} terminada{ROUNDS !== 1 ? 's' : ''}</p>
			<button class="btn-start" onclick={rebuildAndReset}>Volver a empezar</button>
		</div>
	{/if}

	<details class="config-settings" class:disabled={running}>
		<summary>Configurar</summary>
		<div class="config-panel">
			{#each [
				{ key: 'exercises',     label: 'Ejercicios'          },
				{ key: 'exerciseMin',   label: 'Min / ejercicio'     },
				{ key: 'pauseSec',      label: 'Pausa (s)'           },
				{ key: 'rounds',        label: 'Rondas'              },
				{ key: 'roundBreakSec', label: 'Descanso rounds (s)' },
			] as row}
				<div class="cfg-row">
					<span class="cfg-label">{row.label}</span>
					<div class="stepper">
						<button onclick={() => adjustCfg(row.key as keyof typeof cfg, -1)} disabled={running}>−</button>
						<span>{cfg[row.key as keyof typeof cfg]}</span>
						<button onclick={() => adjustCfg(row.key as keyof typeof cfg, 1)} disabled={running}>+</button>
					</div>
				</div>
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
	.dots { display: flex; align-items: center; gap: 5px; margin-bottom: 16px; flex-wrap: wrap; justify-content: center; max-width: 340px; }
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
