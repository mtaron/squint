import { readFileSync } from "node:fs";
import { createClient } from "redis";
import { REDIS_URL } from "$app/env/private";

function tlsOptionsFromUrl(url: URL) {
  const readParam = (name: string) => {
    const path = url.searchParams.get(name);
    return path ? readFileSync(path) : undefined;
  };
  return {
    ca: readParam("ssl_ca_certs"),
    cert: readParam("ssl_certfile"),
    key: readParam("ssl_keyfile"),
  };
}

function createDragonflyClient() {
  const url = new URL(REDIS_URL);
  const tls = url.protocol === "rediss:";
  const client = createClient({
    socket: {
      host: url.hostname,
      port: Number(url.port || 6379),
      ...(tls ? { tls: true, ...tlsOptionsFromUrl(url) } : { tls: false }),
    },
  });
  client.on("error", (error) => console.error("Dragonfly client error", error));
  return client;
}

type DragonflyClient = ReturnType<typeof createDragonflyClient>;

let connection: Promise<DragonflyClient> | undefined;

export function getDragonfly(): Promise<DragonflyClient> {
  connection ??= createDragonflyClient()
    .connect()
    .catch((error) => {
      connection = undefined;
      throw error;
    });
  return connection;
}
