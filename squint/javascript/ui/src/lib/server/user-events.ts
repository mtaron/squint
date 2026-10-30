import { getDragonfly } from "#lib/server/dragonfly.ts";

/** Per-user Dragonfly channels, so a live query sees events from whichever UI replica handled the upload. */
export const channels = {
  uploads: (userId: string) => `squint:uploads:${userId}`,
  documents: (userId: string) => `squint:documents:${userId}`,
};

export async function publish(channel: string, message: unknown): Promise<void> {
  await (await getDragonfly()).publish(channel, JSON.stringify(message));
}

/** Calls `listener` with each message until `signal` aborts. */
export async function subscribe<T>(
  channel: string,
  listener: (message: T) => void,
  signal: AbortSignal,
): Promise<void> {
  // A connection in subscriber mode can't run other commands, so each subscription gets its own
  const subscriber = (await getDragonfly()).duplicate();
  subscriber.on("error", (error) => console.error("Dragonfly subscriber error", error));
  await subscriber.connect();
  signal.addEventListener("abort", () => subscriber.destroy(), { once: true });
  if (signal.aborted) {
    subscriber.destroy();
    return;
  }
  await subscriber.subscribe(channel, (message) => listener(JSON.parse(message) as T));
}

/** Lets a live query sleep until something it reports on changes, or its request ends. */
export class Changes {
  #pending = false;
  #wake: (() => void) | undefined;

  notify(): void {
    this.#pending = true;
    this.#wake?.();
  }

  async next(signal: AbortSignal): Promise<void> {
    if (!this.#pending && !signal.aborted) {
      await new Promise<void>((resolve) => {
        this.#wake = resolve;
        signal.addEventListener("abort", () => resolve(), { once: true });
      });
    }
    this.#pending = false;
    this.#wake = undefined;
  }
}
