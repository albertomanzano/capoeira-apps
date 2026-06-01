import { writable } from 'svelte/store';
import { supabase } from '$lib/supabase';
import type { User } from '@supabase/supabase-js';

export const user    = writable<User | null>(null);
export const role    = writable<string | null>(null);
export const loading = writable(true);

async function loadRole(userId: string) {
	const { data } = await supabase.from('profiles').select('role').eq('id', userId).single();
	role.set(data?.role ?? null);
}

supabase.auth.getSession().then(({ data }) => {
	const u = data.session?.user ?? null;
	user.set(u);
	if (u) loadRole(u.id).finally(() => loading.set(false));
	else loading.set(false);
});

supabase.auth.onAuthStateChange((_, session) => {
	const u = session?.user ?? null;
	user.set(u);
	if (u) loadRole(u.id);
	else role.set(null);
});
