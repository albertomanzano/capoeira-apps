<script lang="ts">
	import { user, role, loading } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { children } = $props();

	$effect(() => {
		if ($loading) return;
		if (!$user) { goto('/login'); return; }
		const path = $page.url.pathname;
		if ($role !== 'profe' && (path === '/members/alumnos' || path.startsWith('/members/alumnos/'))) {
			goto('/members/rutinas');
		}
	});
</script>

{@render children()}
