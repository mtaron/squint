import { describe, expect, test } from "vitest";
import { MAX_PDF_BYTES, fileProblem } from "./upload-limits.ts";

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
