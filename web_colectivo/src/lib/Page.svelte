<script lang="ts">
	let { title, back, children } = $props<{ title: string; back: string; children: any }>();
</script>

<div class="page">
	<div class="header">
		<a href={back} class="back">←</a>
		<h1>{title}</h1>
	</div>
	<div class="content">
		{@render children()}
	</div>
</div>

<style>
	.page { max-width: 480px; margin: 0 auto; min-height: 100vh; display: flex; flex-direction: column; }
	.header {
		display: flex; align-items: center; gap: 12px;
		padding: 16px; border-bottom: 1px solid #1a1a1a;
		position: sticky; top: 0; background: #0f0f0f; z-index: 10;
	}
	h1 { flex: 1; font-size: 1.3rem; font-weight: 700; }
	.back {
		color: #666; font-size: 1.3rem; text-decoration: none;
		padding: 4px 8px; line-height: 1;
	}
	.content { flex: 1; padding: 16px; overflow-y: auto; }
</style>
