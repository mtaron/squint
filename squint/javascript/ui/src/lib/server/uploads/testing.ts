import { PassThrough, Readable } from "node:stream";
import type { ObjectWriter } from "./store.ts";

export function pdfBytes(body = "squint test document"): Uint8Array {
  return new TextEncoder().encode(`%PDF-1.7\n${body}\n%%EOF\n`);
}

export function chunked(bytes: Uint8Array, size = 7): Readable {
  return Readable.from(
    (function* () {
      for (let start = 0; start < bytes.length; start += size) {
        yield bytes.subarray(start, start + size);
      }
    })(),
  );
}

export class MemoryWriter implements ObjectWriter {
  body = new PassThrough();
  chunks: Buffer[] = [];
  aborted = false;
  finished = false;

  constructor() {
    this.body.on("data", (chunk: Buffer) => this.chunks.push(chunk));
  }

  async done() {
    if (!this.body.readableEnded) await new Promise((resolve) => this.body.once("end", resolve));
    this.finished = true;
  }

  async abort() {
    this.aborted = true;
    this.body.destroy();
  }

  get bytes(): Buffer {
    return Buffer.concat(this.chunks);
  }
}
