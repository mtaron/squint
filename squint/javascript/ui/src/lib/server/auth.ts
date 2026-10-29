import { ORIGIN, BETTER_AUTH_SECRET } from "$app/env/private";
import { building } from "$app/env";
import { betterAuth } from "better-auth/minimal";
import type { SecondaryStorage } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { admin } from "better-auth/plugins/admin";
import { sveltekitCookies } from "better-auth/svelte-kit";
import { getRequestEvent } from "$app/server";
import { db } from "#lib/server/db/index.ts";
import { getDragonfly } from "#lib/server/dragonfly.ts";
import { userResources } from "#lib/server/user-resources.ts";

const KEY_PREFIX = "better-auth:";

const dragonflyStorage: SecondaryStorage = {
  async get(key) {
    return (await getDragonfly()).get(KEY_PREFIX + key);
  },
  async getAndDelete(key) {
    return (await getDragonfly()).getDel(KEY_PREFIX + key);
  },
  async increment(key, ttl) {
    const prefixed = KEY_PREFIX + key;
    const [, count] = await (
      await getDragonfly()
    )
      .multi()
      .set(prefixed, 0, { condition: "NX", expiration: { type: "EX", value: ttl } })
      .incr(prefixed)
      .exec();
    return Number(count);
  },
  async set(key, value, ttl) {
    const dragonfly = await getDragonfly();
    await (ttl
      ? dragonfly.set(KEY_PREFIX + key, value, { expiration: { type: "EX", value: ttl } })
      : dragonfly.set(KEY_PREFIX + key, value));
  },
  async delete(key) {
    await (await getDragonfly()).del(KEY_PREFIX + key);
  },
};

export const auth = betterAuth({
  baseURL: ORIGIN,
  // Better Auth rejects a missing secret when the build analyses this module; no request uses it then
  secret: building ? "unused-while-building" : BETTER_AUTH_SECRET,
  database: drizzleAdapter(db, { provider: "pg" }),
  secondaryStorage: dragonflyStorage,
  // Per-user S3 bucket names embed the user id, and bucket names must be lowercase
  advanced: { database: { generateId: "uuid" } },
  emailAndPassword: { enabled: true },
  plugins: [
    userResources(),
    admin(),
    sveltekitCookies(getRequestEvent), // make sure this is the last plugin in the array
  ],
});
