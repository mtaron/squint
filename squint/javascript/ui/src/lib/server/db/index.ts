import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';
import { PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE } from '$app/env/private';

export function connect(options: postgres.Options<{}> = {}) {
	return postgres({
		host: PGHOST,
		port: PGPORT,
		user: PGUSER,
		password: PGPASSWORD,
		database: PGDATABASE,
		ssl: 'prefer',
		...options
	});
}

export const client = connect();

export const db = drizzle(client, { schema });
