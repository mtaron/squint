import { createHash } from "node:crypto";
import { once } from "node:events";
import type { Writable } from "node:stream";

export interface ObjectWriter {
  body: Writable;
  done(): Promise<void>;
  abort(): Promise<void>;
}

export type CreateObjectWriter = (key: string) => ObjectWriter;

export type StoredPdf = { ok: true; sha256: string; sizeBytes: number };
export type RejectedPdf = { ok: false; reason: "not_pdf" | "too_large" | "empty" };

const PDF_MAGIC = Buffer.from("%PDF-");
const MAGIC_SEARCH_BYTES = 1024;

/**
 * Streams `source` into `writer` while hashing it, after checking that it starts like a PDF.
 * Always reads `source` to the end, so a rejected file doesn't stall the request it came from.
 */
export async function storePdf(
  source: AsyncIterable<Uint8Array>,
  writer: ObjectWriter,
  maxBytes: number,
): Promise<StoredPdf | RejectedPdf> {
  const hash = createHash("sha256");
  let head: Buffer | undefined = Buffer.alloc(0);
  let sizeBytes = 0;
  let rejection: RejectedPdf["reason"] | undefined;

  async function write(chunk: Buffer) {
    hash.update(chunk);
    if (!writer.body.write(chunk)) await once(writer.body, "drain");
  }

  async function reject(reason: RejectedPdf["reason"]) {
    rejection = reason;
    head = undefined;
    await writer.abort();
  }

  try {
    for await (const chunk of source) {
      if (rejection) continue;
      sizeBytes += chunk.byteLength;
      if (sizeBytes > maxBytes) {
        await reject("too_large");
        continue;
      }
      if (head === undefined) {
        await write(Buffer.from(chunk));
        continue;
      }
      head = Buffer.concat([head, chunk]);
      if (head.length < MAGIC_SEARCH_BYTES) continue;
      if (!head.subarray(0, MAGIC_SEARCH_BYTES).includes(PDF_MAGIC)) {
        await reject("not_pdf");
        continue;
      }
      const buffered = head;
      head = undefined;
      await write(buffered);
    }

    if (!rejection && head !== undefined) {
      if (head.length === 0) await reject("empty");
      else if (!head.includes(PDF_MAGIC)) await reject("not_pdf");
      else await write(head);
    }
    if (rejection) return { ok: false, reason: rejection };

    writer.body.end();
    await writer.done();
    return { ok: true, sha256: hash.digest("hex"), sizeBytes };
  } catch (error) {
    if (!rejection) await writer.abort().catch(() => {});
    throw error;
  }
}
