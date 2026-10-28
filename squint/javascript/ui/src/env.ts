import { defineEnvVars } from "@sveltejs/kit/env";
import { building } from "$app/env";
import * as v from "valibot";

// The build analyses server code without a deployment environment, so values are only required when the app starts
function requiredAtRuntime<TSchema extends v.GenericSchema<string, unknown>>(
  schema: TSchema,
): TSchema {
  return (building ? v.optional(schema) : schema) as TSchema;
}

const text = requiredAtRuntime(v.pipe(v.string(), v.nonEmpty()));
const url = requiredAtRuntime(v.pipe(v.string(), v.url()));

export const variables = defineEnvVars({
  PGHOST: { schema: text },
  PGPORT: {
    schema: requiredAtRuntime(
      v.pipe(v.string(), v.toNumber(), v.integer(), v.minValue(1), v.maxValue(65535)),
    ),
  },
  PGUSER: { schema: text },
  PGPASSWORD: { schema: text },
  PGDATABASE: { schema: text },
  TEMPORAL_ADDRESS: { description: "Temporal frontend address as `host:port`.", schema: text },
  TEMPORAL_TLS_SERVER_CA_CERT_PATH: {
    description: "Path to the CA certificate that signed the Temporal frontend's certificate.",
    schema: text,
  },
  REDIS_URL: {
    description:
      "Dragonfly URL. TLS files are given as `ssl_ca_certs`, `ssl_certfile` and `ssl_keyfile` query parameters, as redis-py expects.",
    schema: url,
  },
  ORIGIN: {
    description: "The app origin (base URL), e.g. `https://squint.loc`.",
    schema: url,
  },
  BETTER_AUTH_SECRET: {
    description:
      "Secret used to sign tokens. Use at least 32 characters generated with high entropy. See [Better Auth installation](https://www.better-auth.com/docs/installation).",
    schema: requiredAtRuntime(v.pipe(v.string(), v.minLength(32))),
  },
  AWS_ENDPOINT_URL: { schema: url },
  AWS_REGION: { schema: text },
  AWS_ACCESS_KEY_ID: { schema: text },
  AWS_SECRET_ACCESS_KEY: { schema: text },
});
