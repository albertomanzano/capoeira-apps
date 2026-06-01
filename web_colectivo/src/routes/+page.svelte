<script lang="ts">
	import { goto } from '$app/navigation';
	import { user, loading } from '$lib/stores/auth';

	$effect(() => {
		if ($loading) return;
		goto($user ? '/rutinas' : '/login');
	});
</script>
