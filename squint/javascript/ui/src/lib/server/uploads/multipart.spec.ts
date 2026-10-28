import { Readable } from "node:stream";
import { setTimeout as sleep } from "node:timers/promises";
import { describe, expect, it } from "vitest";
import { relay } from "./multipart.ts";

describe("relay", () => {
  it("passes a large part through a slow consumer without piling up listeners", async () => {
    const chunk = Buffer.alloc(64 * 1024, 1);
    const part = Readable.from(Array.from({ length: 50 }, () => chunk));
    const { stream, drained } = relay(part);

    let received = 0;
    let maxListeners = 0;
    for await (const piece of stream) {
      received += (piece as Buffer).length;
      maxListeners = Math.max(maxListeners, stream.listenerCount("close"));
      await sleep(1);
    }
    await drained;

    expect(received).toBe(50 * chunk.length);
    expect(maxListeners).toBeLessThan(5);
  });

  it("keeps reading the part after its consumer gives up", async () => {
    const part = Readable.from(Array.from({ length: 50 }, () => Buffer.alloc(64 * 1024)));
    const { stream, drained } = relay(part);

    stream.destroy();
    await drained;

    expect(part.readableEnded).toBe(true);
  });
});
