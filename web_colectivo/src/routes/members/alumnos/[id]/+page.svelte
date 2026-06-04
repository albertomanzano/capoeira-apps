<script lang="ts">
	import { supabase } from '$lib/supabase';
	import { page } from '$app/stores';
	import Page from '$lib/Page.svelte';

	const studentId = $derived($page.params.id);
	let studentName = $state('');

	async function load() {
		const { data } = await supabase
			.from('students')
			.select('name')
			.eq('id', studentId)
			.single();
		studentName = data?.name ?? '';
	}

	$effect(() => { load(); });
</script>

<Page title={studentName || '…'} back="/alumnos">
	<p class="hint">El alumno gestiona sus propios entrenamientos.</p>
</Page>

<style>
	.hint { color: #444; text-align: center; padding: 60px 0; font-size: 0.9rem; }
</style>
