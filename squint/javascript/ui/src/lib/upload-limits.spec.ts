import * as v from "valibot";
import { describe, expect, test } from "vitest";
import { MAX_PDF_BYTES, fileProblem, uploadSchema } from "./upload-limits.ts";

describe("fileProblem", () => {
  test("accepts PDFs regardless of the extension's case", () => {
    expect(fileProblem({ name: "Invoice.PDF", size: 10 })).toBeUndefined();
  });

  test("rejects files that aren't PDFs", () => {
    expect(fileProblem({ name: "notes.txt", size: 10 })).toBe(
      "This isn't a PDF. Only PDF files can be uploaded.",
    );
  });

  test("skips empty files", () => {
    expect(fileProblem({ name: "blank.pdf", size: 0 })).toBe(
      "This PDF is empty, so it was skipped.",
    );
  });

  test("rejects PDFs over 500 MB", () => {
    expect(fileProblem({ name: "huge.pdf", size: MAX_PDF_BYTES })).toBeUndefined();
    expect(fileProblem({ name: "huge.pdf", size: MAX_PDF_BYTES + 1 })).toMatch(
      /larger than 500 MB/,
    );
  });
});

describe("uploadSchema", () => {
  const pdf = (size: number) => new File([new Uint8Array(size)], "a.pdf");

  test("requires at least one file", () => {
    expect(v.safeParse(uploadSchema, { files: [] }).success).toBe(false);
  });

  test("limits the number of files per request", () => {
    const files = Array.from({ length: 1001 }, () => pdf(1));
    expect(v.safeParse(uploadSchema, { files }).success).toBe(false);
    expect(v.safeParse(uploadSchema, { files: files.slice(1) }).success).toBe(true);
  });

  test("limits the total size of a request", () => {
    const large = Object.defineProperty(pdf(1), "size", { value: 1024 ** 3 + 1 });
    expect(v.safeParse(uploadSchema, { files: [large, large] }).success).toBe(false);
  });
});
