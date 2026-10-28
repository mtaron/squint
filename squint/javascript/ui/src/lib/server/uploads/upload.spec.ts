import { describe, expect, it } from "vitest";
import { zipSync } from "fflate";
import { MAX_FILES_PER_REQUEST } from "#lib/uploads/limits.ts";
import type { NewDocument, Replacement, SaveResult } from "./documents.ts";
import { parseMultipart, UploadLimitError } from "./multipart.ts";
import { MemoryWriter, pdfBytes } from "./testing.ts";
import { receiveReplacement, receiveUploads, type UploadServices } from "./upload.ts";

class FakeServices implements UploadServices {
  userId = "user-1";
  objects = new Map<string, MemoryWriter>();
  deleted: string[] = [];
  documents: NewDocument[] = [];
  replacements: Replacement[] = [];
  ingested: string[] = [];

  writeObject(key: string) {
    const writer = new MemoryWriter();
    this.objects.set(key, writer);
    return writer;
  }

  async deleteObject(key: string) {
    this.deleted.push(key);
  }

  async insertDocument(values: NewDocument): Promise<SaveResult> {
    const existing = this.documents.find((doc) => doc.sha256 === values.sha256);
    if (existing) return { saved: false, existingName: existing.name };
    this.documents.push(values);
    return { saved: true };
  }

  async replaceDocument(values: Replacement): Promise<SaveResult> {
    const other = this.documents.find(
      (doc) => doc.sha256 === values.sha256 && doc.id !== values.id,
    );
    if (other) return { saved: false, existingName: other.name };
    this.replacements.push(values);
    return { saved: true };
  }

  async startIngestion(documentId: string) {
    this.ingested.push(documentId);
  }
}

function multipartRequest(files: [field: string, name: string, data: Uint8Array | string][]) {
  const form = new FormData();
  for (const [field, name, data] of files) {
    if (typeof data === "string") form.append(field, data);
    else form.append(field, new File([data as Uint8Array<ArrayBuffer>], name));
  }
  return new Request("http://squint.test/?/upload", { method: "POST", body: form });
}

function parts(request: Request, limits = {}) {
  return parseMultipart(request, {
    files: MAX_FILES_PER_REQUEST,
    fileSize: 10_000_000,
    totalBytes: 10_000_000,
    ...limits,
  });
}

describe("receiveUploads", () => {
  it("stores PDFs from files and archives and reports everything else", async () => {
    const services = new FakeServices();
    const archive = zipSync({
      "papers/one.pdf": pdfBytes("one"),
      "papers/notes.txt": new TextEncoder().encode("notes"),
    });
    const request = multipartRequest([
      ["files", "two.pdf", pdfBytes("two")],
      ["files", "papers.zip", archive],
      ["files", "logo.png", new Uint8Array([1, 2, 3])],
      ["files", "fake.pdf", new TextEncoder().encode("not really")],
      ["files", ".DS_Store", new Uint8Array([0])],
    ]);

    const outcome = await receiveUploads(parts(request), services);

    expect(outcome.added.map(({ name }) => name)).toEqual(["two.pdf", "one.pdf"]);
    expect(outcome.skipped).toEqual(["notes.txt", "logo.png"]);
    expect(outcome.rejected).toEqual([{ name: "fake.pdf", reason: "This file isn't a PDF." }]);
    expect(services.ingested).toEqual(outcome.added.map(({ id }) => id));
    const stored = services.objects.get(services.documents[0].objectKey);
    expect(stored?.bytes.equals(Buffer.from(pdfBytes("two")))).toBe(true);
  });

  it("skips the empty part a native form sends for an unused file input", async () => {
    const form = new FormData();
    form.append("files", new File([pdfBytes() as Uint8Array<ArrayBuffer>], "a.pdf"));
    form.append("files", new File([], ""));
    form.append("files", new File([pdfBytes("b") as Uint8Array<ArrayBuffer>], "b.pdf"));
    const request = new Request("http://squint.test/?/upload", { method: "POST", body: form });

    const outcome = await receiveUploads(parts(request), new FakeServices());

    expect(outcome.added.map(({ name }) => name)).toEqual(["a.pdf", "b.pdf"]);
  });

  it("reports a PDF the user already has as a duplicate and deletes the new copy", async () => {
    const services = new FakeServices();
    await receiveUploads(parts(multipartRequest([["files", "a.pdf", pdfBytes()]])), services);
    const outcome = await receiveUploads(
      parts(multipartRequest([["files", "a-copy.pdf", pdfBytes()]])),
      services,
    );

    expect(outcome.added).toEqual([]);
    expect(outcome.duplicates).toEqual([{ name: "a-copy.pdf", existingName: "a.pdf" }]);
    expect(services.deleted).toHaveLength(1);
    expect(services.ingested).toHaveLength(1);
  });

  it("rejects a corrupt archive and keeps going", async () => {
    const services = new FakeServices();
    const truncated = zipSync({ "a.pdf": pdfBytes("x".repeat(5000)) }).subarray(0, 60);
    const outcome = await receiveUploads(
      parts(
        multipartRequest([
          ["files", "broken.zip", truncated],
          ["files", "b.pdf", pdfBytes("b")],
        ]),
      ),
      services,
    );

    expect(outcome.rejected.map(({ name }) => name)).toEqual(["broken.zip"]);
    expect(outcome.added.map(({ name }) => name)).toEqual(["b.pdf"]);
  });

  it("stops at the file limit", async () => {
    const request = multipartRequest([
      ["files", "a.pdf", pdfBytes("a")],
      ["files", "b.pdf", pdfBytes("b")],
    ]);
    await expect(
      receiveUploads(parts(request, { files: 1 }), new FakeServices()),
    ).rejects.toBeInstanceOf(UploadLimitError);
  });
});

describe("receiveReplacement", () => {
  it("stores the new PDF under the existing document", async () => {
    const services = new FakeServices();
    const result = await receiveReplacement(
      parts(multipartRequest([["file", "unlocked.pdf", pdfBytes("unlocked")]])),
      "doc-1",
      services,
    );

    expect(result).toMatchObject({ replaced: true, name: "unlocked.pdf" });
    expect(services.replacements).toMatchObject([{ id: "doc-1", name: "unlocked.pdf" }]);
  });

  it("refuses a PDF that matches a different document", async () => {
    const services = new FakeServices();
    await receiveUploads(parts(multipartRequest([["files", "other.pdf", pdfBytes()]])), services);
    const result = await receiveReplacement(
      parts(multipartRequest([["file", "same.pdf", pdfBytes()]])),
      "doc-1",
      services,
    );

    expect(result).toEqual({
      replaced: false,
      outcome: expect.objectContaining({
        duplicates: [{ name: "same.pdf", existingName: "other.pdf" }],
      }),
    });
  });
});
