import { createHash } from "node:crypto";
import { describe, expect, it } from "vitest";
import { storePdf } from "./store.ts";
import { chunked, MemoryWriter, pdfBytes } from "./testing.ts";

describe("storePdf", () => {
  it("stores a PDF and returns its hash and size", async () => {
    const bytes = pdfBytes("x".repeat(5000));
    const writer = new MemoryWriter();
    const stored = await storePdf(chunked(bytes, 333), writer, 1_000_000);
    expect(stored).toEqual({
      ok: true,
      sha256: createHash("sha256").update(bytes).digest("hex"),
      sizeBytes: bytes.length,
    });
    expect(writer.bytes.equals(Buffer.from(bytes))).toBe(true);
  });

  it("accepts a header after leading junk within the first kilobyte", async () => {
    const bytes = Buffer.concat([Buffer.alloc(100, 0x20), pdfBytes()]);
    const stored = await storePdf(chunked(bytes), new MemoryWriter(), 1_000_000);
    expect(stored.ok).toBe(true);
  });

  it("rejects a file that isn't a PDF and reads it to the end", async () => {
    const source = chunked(Buffer.alloc(5000, 0x41));
    const writer = new MemoryWriter();
    const stored = await storePdf(source, writer, 1_000_000);
    expect(stored).toEqual({ ok: false, reason: "not_pdf" });
    expect(writer.aborted).toBe(true);
    expect(source.readableEnded).toBe(true);
  });

  it("rejects a PDF over the size limit", async () => {
    const writer = new MemoryWriter();
    const stored = await storePdf(chunked(pdfBytes("x".repeat(2000)), 100), writer, 1500);
    expect(stored).toEqual({ ok: false, reason: "too_large" });
    expect(writer.aborted).toBe(true);
  });

  it("rejects an empty file", async () => {
    const stored = await storePdf(chunked(new Uint8Array()), new MemoryWriter(), 1000);
    expect(stored).toEqual({ ok: false, reason: "empty" });
  });
});
