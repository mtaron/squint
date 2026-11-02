import { createHash } from "node:crypto";
import { documentObjectKey, isDocumentId } from "@squint/db/storage";
import { describe, expect, test } from "vitest";
import {
  documentStore,
  type DocumentStoreDependencies,
  type NewDocument,
} from "./document-store.ts";

const USER_ID = "0f8fad5b-d9cb-469f-a165-70867728950e";
const BUCKET = `squint-u-${USER_ID}`;
const CONTENTS = "%PDF-1.7 a tiny pdf";
const SHA256 = createHash("sha256").update(CONTENTS).digest("hex");

function fakes(overrides: Partial<DocumentStoreDependencies> = {}) {
  const objects = new Map<string, string>();
  const rows: NewDocument[] = [];
  const calls: string[] = [];
  const dependencies: DocumentStoreDependencies = {
    storage: {
      async put(bucket, key, body) {
        objects.set(`${bucket}/${key}`, await new Response(body).text());
      },
      async delete(bucket, key) {
        objects.delete(`${bucket}/${key}`);
      },
    },
    async insert(row) {
      const existing = rows.find(({ sha256 }) => sha256 === row.sha256);
      if (existing) {
        return { duplicateOf: existing.name };
      }
      rows.push(row);
      return {};
    },
    async remove(documentId) {
      calls.push(`remove ${documentId}`);
    },
    async startIngestion(input) {
      calls.push(`startIngestion ${input.documentId}`);
    },
    async announce(_userId, { id }) {
      calls.push(`announce ${id}`);
    },
    async removeOwned(userId, documentIds, afterRemoving) {
      calls.push(`removeOwned ${userId} ${documentIds.join(" ")}`);
      await afterRemoving(
        documentIds.map((id) => ({ id, pageCount: id === "ingesting" ? null : 3 })),
      );
    },
    async startCleanup({ userId, documentIds }) {
      calls.push(`startCleanup ${userId} ${documentIds.join(" ")}`);
    },
    ...overrides,
  };
  return { store: documentStore(dependencies), objects, rows, calls };
}

const pdf = (name = "a.pdf") => new File([CONTENTS], name);

describe("documentStore.add", () => {
  test("gives each document a short id that its objects live under", async () => {
    const { store, objects } = fakes();

    const outcome = await store.add(USER_ID, pdf());

    if (!("documentId" in outcome)) {
      throw new Error(outcome.problem);
    }
    expect(isDocumentId(outcome.documentId)).toBe(true);
    expect(outcome.documentId).toHaveLength(10);
    expect(documentObjectKey(outcome.documentId)).toBe(
      `documents/${outcome.documentId}/original.pdf`,
    );
    expect(objects.has(`${BUCKET}/${documentObjectKey(outcome.documentId)}`)).toBe(true);
  });

  test("streams the file to the user's bucket, records it, and starts ingesting it", async () => {
    const { store, objects, rows, calls } = fakes();

    const outcome = await store.add(USER_ID, pdf());

    if (!("documentId" in outcome)) throw new Error(outcome.problem);
    const { documentId } = outcome;
    expect(objects).toEqual(
      new Map([[`${BUCKET}/documents/${documentId}/original.pdf`, CONTENTS]]),
    );
    expect(rows).toEqual([
      {
        id: documentId,
        userId: USER_ID,
        name: "a.pdf",
        sha256: SHA256,
        sizeBytes: CONTENTS.length,
      },
    ]);
    expect(calls).toEqual([`startIngestion ${documentId}`, `announce ${documentId}`]);
  });

  test("skips a file the user already uploaded and deletes the copy", async () => {
    const { store, objects, rows } = fakes();
    await store.add(USER_ID, pdf("original.pdf"));

    const outcome = await store.add(USER_ID, pdf("copy.pdf"));

    expect(outcome).toEqual({
      problem: "Already uploaded as original.pdf, so it was skipped.",
    });
    expect(objects.size).toBe(1);
    expect(rows.map(({ name }) => name)).toEqual(["original.pdf"]);
  });

  test("rejects files that aren't PDFs without storing them", async () => {
    const { store, objects } = fakes();

    const outcome = await store.add(USER_ID, new File(["hi"], "notes.txt"));

    expect(outcome).toEqual({ problem: "This isn't a PDF. Only PDF files can be uploaded." });
    expect(objects.size).toBe(0);
  });

  test("cleans up when ingestion can't start", async () => {
    const { store, objects, calls } = fakes({
      async startIngestion() {
        throw new Error("Temporal is down");
      },
    });

    const outcome = await store.add(USER_ID, pdf());

    expect(outcome).toEqual({ problem: "This PDF couldn't be processed. Try again." });
    expect(objects.size).toBe(0);
    expect(calls).toEqual([expect.stringMatching(/^remove /)]);
  });
});

describe("documentStore.delete", () => {
  test("removes the rows, then has the worker remove the files", async () => {
    const { store, calls } = fakes();

    await store.delete(USER_ID, ["first", "second"]);

    expect(calls).toEqual([
      `removeOwned ${USER_ID} first second`,
      `startCleanup ${USER_ID} first second`,
    ]);
  });

  test("leaves a document that's still ingesting to its workflow", async () => {
    const { store, calls } = fakes();

    await store.delete(USER_ID, ["ingesting", "second"]);

    expect(calls).toContain(`startCleanup ${USER_ID} second`);
  });

  test("starts no cleanup when nothing is ingested", async () => {
    const { store, calls } = fakes();

    await store.delete(USER_ID, ["ingesting"]);

    expect(calls).toEqual([`removeOwned ${USER_ID} ingesting`]);
  });

  test("only cleans up what was actually removed", async () => {
    const { store, calls } = fakes({
      async removeOwned(_userId, _documentIds, afterRemoving) {
        await afterRemoving([]);
      },
    });

    await store.delete(USER_ID, ["someone-elses"]);

    expect(calls).toEqual([]);
  });

  test("fails inside the removal, so the rows are restored if cleanup can't start", async () => {
    let failure: unknown;
    const { store } = fakes({
      async removeOwned(_userId, documentIds, afterRemoving) {
        try {
          await afterRemoving(documentIds.map((id) => ({ id, pageCount: 3 })));
        } catch (error) {
          failure = error;
          throw error;
        }
      },
      async startCleanup() {
        throw new Error("Temporal is down");
      },
    });

    await expect(store.delete(USER_ID, ["first"])).rejects.toThrow("Temporal is down");
    expect(failure).toBeInstanceOf(Error);
  });
});
