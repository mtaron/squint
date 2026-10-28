import { once } from "node:events";
import { PassThrough, Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
import { createGunzip } from "node:zlib";
import { Unzip, UnzipInflate } from "fflate";
import tar from "tar-stream";
import { classifyName, isSystemFile, MAX_ARCHIVE_EXPANDED_BYTES } from "#lib/uploads/limits.ts";

export type ArchiveKind = "zip" | "tar" | "tar.gz";

export type ArchiveEntryHandler = (path: string, stream: Readable) => Promise<void>;

export class ArchiveError extends Error {}

/**
 * Streams the PDFs out of an archive one at a time, handing each to `onPdf` and reporting other
 * files to `onSkipped`. Nested archives are skipped rather than unpacked.
 */
export async function unpackArchive(
  kind: ArchiveKind,
  source: AsyncIterable<Uint8Array>,
  onPdf: ArchiveEntryHandler,
  onSkipped: (path: string) => void,
): Promise<void> {
  const countExpanded = expansionGuard();
  if (kind === "zip") {
    await unpackZip(source, onPdf, onSkipped, countExpanded);
  } else {
    await unpackTar(kind === "tar.gz", source, onPdf, onSkipped, countExpanded);
  }
}

function expansionGuard() {
  let total = 0;
  return (bytes: number) => {
    total += bytes;
    if (total > MAX_ARCHIVE_EXPANDED_BYTES) {
      throw new ArchiveError("the archive expands to more than the size limit");
    }
  };
}

function reportUnlessPdf(path: string, onSkipped: (path: string) => void): boolean {
  if (classifyName(path) === "pdf") return false;
  if (!path.endsWith("/") && !isSystemFile(path)) onSkipped(path);
  return true;
}

async function unpackZip(
  source: AsyncIterable<Uint8Array>,
  onPdf: ArchiveEntryHandler,
  onSkipped: (path: string) => void,
  countExpanded: (bytes: number) => void,
) {
  const unzip = new Unzip();
  unzip.register(UnzipInflate);
  const handlers: Promise<void>[] = [];
  const openEntries = new Set<PassThrough>();
  let backpressure: Promise<unknown> | undefined;
  let failure: unknown;

  function fail(error: unknown) {
    failure ??= error;
    for (const entry of openEntries) entry.destroy(toArchiveError(failure));
    openEntries.clear();
  }

  unzip.onfile = (file) => {
    if (reportUnlessPdf(file.name, onSkipped)) return;
    const entry = new PassThrough();
    openEntries.add(entry);
    file.ondata = (error, chunk, final) => {
      if (failure) return;
      try {
        if (error) throw error;
        countExpanded(chunk.byteLength);
      } catch (entryError) {
        file.terminate();
        fail(entryError);
        return;
      }
      if (!entry.write(chunk)) backpressure = once(entry, "drain");
      if (final) {
        openEntries.delete(entry);
        entry.end();
      }
    };
    handlers.push(onPdf(file.name, entry));
    file.start();
  };

  try {
    for await (const chunk of source) {
      if (failure) continue;
      unzip.push(chunk);
      if (backpressure) {
        await backpressure;
        backpressure = undefined;
      }
    }
    if (!failure) unzip.push(new Uint8Array(0), true);
  } catch (error) {
    fail(error);
  }
  if (openEntries.size > 0) fail(new ArchiveError("the archive ended in the middle of a file"));
  const results = await Promise.allSettled(handlers);
  if (failure) throw toArchiveError(failure);
  for (const result of results) {
    if (result.status === "rejected") throw result.reason;
  }
}

async function unpackTar(
  gzipped: boolean,
  source: AsyncIterable<Uint8Array>,
  onPdf: ArchiveEntryHandler,
  onSkipped: (path: string) => void,
  countExpanded: (bytes: number) => void,
) {
  const extract = tar.extract();
  extract.on("entry", (header, stream, next) => {
    if (header.type !== "file" || reportUnlessPdf(header.name, onSkipped)) {
      stream.on("end", () => next()).resume();
      return;
    }
    const counted = new PassThrough();
    stream.on("data", (chunk) => {
      try {
        countExpanded((chunk as Buffer).length);
      } catch (error) {
        extract.destroy(error as Error);
      }
    });
    stream.on("error", (error: Error) => counted.destroy(error));
    stream.pipe(counted);
    onPdf(header.name, counted).then(
      () => next(),
      (error: Error) => extract.destroy(error),
    );
  });

  const input = Readable.from(source);
  try {
    if (gzipped) await pipeline(input, createGunzip(), extract);
    else await pipeline(input, extract);
  } catch (error) {
    throw toArchiveError(error);
  }
}

function toArchiveError(error: unknown): ArchiveError {
  if (error instanceof ArchiveError) return error;
  const message = error instanceof Error ? error.message : String(error);
  return new ArchiveError(`the archive could not be read: ${message}`);
}
