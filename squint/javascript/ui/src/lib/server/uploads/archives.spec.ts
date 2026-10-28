import { randomBytes } from "node:crypto";
import { buffer } from "node:stream/consumers";
import { gzipSync } from "node:zlib";
import { Zip, ZipDeflate, ZipPassThrough, zipSync } from "fflate";
import tar from "tar-stream";
import { describe, expect, it } from "vitest";
import { ArchiveError, unpackArchive, type ArchiveKind } from "./archives.ts";
import { chunked, pdfBytes } from "./testing.ts";

const files: Record<string, Uint8Array> = {
  "corpus/a.pdf": pdfBytes("a"),
  "corpus/nested/b.PDF": pdfBytes(randomBytes(20_000).toString("hex")),
  "corpus/README.md": new TextEncoder().encode("# corpus"),
  "corpus/logo.png": new Uint8Array([0x89, 0x50, 0x4e, 0x47]),
  "__MACOSX/corpus/._a.pdf": new Uint8Array([0]),
};

async function unpack(kind: ArchiveKind, archive: Uint8Array) {
  const pdfs: Record<string, Buffer> = {};
  const skipped: string[] = [];
  await unpackArchive(
    kind,
    chunked(archive, 1000),
    async (path, stream) => {
      pdfs[path] = await buffer(stream);
    },
    (path) => skipped.push(path),
  );
  return { pdfs, skipped };
}

function expectCorpus({ pdfs, skipped }: Awaited<ReturnType<typeof unpack>>) {
  expect(Object.keys(pdfs).sort()).toEqual(["corpus/a.pdf", "corpus/nested/b.PDF"]);
  expect(pdfs["corpus/nested/b.PDF"].equals(Buffer.from(files["corpus/nested/b.PDF"]))).toBe(true);
  expect(skipped.sort()).toEqual(["corpus/README.md", "corpus/logo.png"]);
}

function streamingZip(entry: (name: string) => ZipDeflate | ZipPassThrough): Promise<Uint8Array> {
  return new Promise((resolve, reject) => {
    const chunks: Uint8Array[] = [];
    const zip = new Zip((error, chunk, final) => {
      if (error) return reject(error);
      chunks.push(chunk);
      if (final) resolve(Buffer.concat(chunks));
    });
    for (const [name, data] of Object.entries(files)) {
      const file = entry(name);
      zip.add(file);
      file.push(data, true);
    }
    zip.end();
  });
}

async function tarball(): Promise<Buffer> {
  const pack = tar.pack();
  for (const [name, data] of Object.entries(files)) pack.entry({ name }, Buffer.from(data));
  pack.finalize();
  return buffer(pack);
}

describe("unpackArchive", () => {
  it("streams PDFs out of a zip", async () => {
    expectCorpus(await unpack("zip", zipSync(files)));
  });

  it("streams PDFs out of a zip written with data descriptors", async () => {
    expectCorpus(await unpack("zip", await streamingZip((name) => new ZipDeflate(name))));
  });

  it("streams PDFs out of a zip with uncompressed entries written with data descriptors", async () => {
    expectCorpus(await unpack("zip", await streamingZip((name) => new ZipPassThrough(name))));
  });

  it("rejects a zip that ends partway through a PDF", async () => {
    const archive = zipSync(files);
    await expect(unpack("zip", archive.subarray(0, 20_000))).rejects.toBeInstanceOf(ArchiveError);
  });

  it("streams PDFs out of a tar", async () => {
    expectCorpus(await unpack("tar", await tarball()));
  });

  it("streams PDFs out of a gzipped tar", async () => {
    expectCorpus(await unpack("tar.gz", gzipSync(await tarball())));
  });

  it("rejects a tar that ends partway through a PDF", async () => {
    const archive = await tarball();
    await expect(unpack("tar", archive.subarray(0, 20_000))).rejects.toBeInstanceOf(ArchiveError);
  });

  it("rejects a gzipped tar that isn't gzipped", async () => {
    await expect(unpack("tar.gz", await tarball())).rejects.toBeInstanceOf(ArchiveError);
  });
});
