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
  PGHOST: { description: "Postgres host.", schema: text },
  PGPORT: {
    description: "Postgres port.",
    schema: requiredAtRuntime(
      v.pipe(v.string(), v.toNumber(), v.integer(), v.minValue(1), v.maxValue(65535)),
    ),
  },
  PGUSER: { description: "Postgres user.", schema: text },
  PGPASSWORD: { description: "Postgres password.", schema: text },
  PGDATABASE: { description: "Postgres database name.", schema: text },
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
  AWS_ENDPOINT_URL: {
    description: "S3 endpoint URL; uploads go to one bucket per user.",
    schema: url,
  },
  AWS_REGION: { description: "S3 region.", schema: text },
  AWS_ACCESS_KEY_ID: { description: "S3 access key, read by the AWS SDK.", schema: text },
  AWS_SECRET_ACCESS_KEY: { description: "S3 secret key, read by the AWS SDK.", schema: text },
  ORIGIN: {
    description: "The app origin (base URL), e.g. `https://squint.loc`.",
    schema: url,
  },
  BETTER_AUTH_SECRET: {
    description:
      "Secret used to sign tokens. Use at least 32 characters generated with high entropy. See [Better Auth installation](https://www.better-auth.com/docs/installation).",
    schema: requiredAtRuntime(v.pipe(v.string(), v.minLength(32))),
  },
});
