import { drizzle } from "drizzle-orm/postgres-js";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import { connect } from "./index";

const MIGRATIONS_FOLDER = "drizzle";
// Arbitrary key shared by every replica so only one migrates at a time
const MIGRATION_LOCK_KEY = 0x5157494e54;

export async function runMigrations() {
  const connection = connect({ max: 1, onnotice: () => {} });
  try {
    await connection`select pg_advisory_lock(${MIGRATION_LOCK_KEY})`;
    await migrate(drizzle(connection), { migrationsFolder: MIGRATIONS_FOLDER });
    await connection`select pg_advisory_unlock(${MIGRATION_LOCK_KEY})`;
  } finally {
    await connection.end();
  }
}
