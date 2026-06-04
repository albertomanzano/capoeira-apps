<script lang="ts">
	import { goto } from '$app/navigation';
	import { role, loading } from '$lib/stores/auth';

	$effect(() => {
		if ($loading) return;
		goto($role === 'profe' ? '/members/alumnos' : '/members/rutinas');
	});
</script>
