<script lang="ts">
	import { goto } from '$app/navigation';
	import { user, role, loading } from '$lib/stores/auth';

	$effect(() => {
		if ($loading) return;
		goto($user ? ($role === 'profe' ? '/alumnos' : '/rutinas') : '/descargas');
	});
</script>
