import { writable, get } from 'svelte/store';
import { supabase } from '$lib/supabase';

export const numSlots = writable(6);

supabase.from('config').select('num_slots').eq('id', 1).single().then(({ data }) => {
	if (data) numSlots.set(data.num_slots);
});

export async function saveNumSlots(n: number) {
	await supabase.from('config').upsert({ id: 1, num_slots: n });
	numSlots.set(n);
}

export { get };
