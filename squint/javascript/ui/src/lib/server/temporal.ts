import { Client, Connection } from '@temporalio/client';
import { TEMPORAL_ADDRESS } from '$app/env/private';

let client: Promise<Client> | undefined;

export function getTemporalClient(): Promise<Client> {
	client ??= Connection.connect({ address: TEMPORAL_ADDRESS })
		.then((connection) => new Client({ connection }))
		.catch((error) => {
			client = undefined;
			throw error;
		});
	return client;
}
