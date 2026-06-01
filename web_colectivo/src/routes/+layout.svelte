<script lang="ts">
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href="/favicon.svg" />
</svelte:head>

<style>
	:global(*) { box-sizing: border-box; margin: 0; padding: 0; }
	:global(body) {
		font-family: system-ui, sans-serif;
		background: #0f0f0f;
		color: #fff;
		min-height: 100vh;
	}
</style>

{@render children()}
