import { page } from "vitest/browser";
import { describe, expect, it } from "vitest";
import { render } from "vitest-browser-svelte";
import type { DocumentSummary } from "#lib/uploads/documents.ts";
import DocumentRow from "./DocumentRow.svelte";

function documentWith(overrides: Partial<DocumentSummary>): DocumentSummary {
  return {
    id: "doc-1",
    name: "contract.pdf",
    sizeBytes: 1000,
    status: "ready",
    pageCount: 12,
    errorCode: null,
    errorDetail: null,
    uploadedAt: new Date("2026-10-26T12:00:00Z"),
    ...overrides,
  };
}

describe("DocumentRow.svelte", () => {
  it("shows the page count of a ready document", async () => {
    render(DocumentRow, { document: documentWith({}), showUploadDate: false });

    // Narrow viewports, like the test frame, hide the page count
    await expect.element(page.getByText("12 pages")).toBeInTheDocument();
    await expect.element(page.getByText("Ready")).toBeVisible();
  });

  it("expands a failed document to explain the problem and offer fixes", async () => {
    render(DocumentRow, {
      document: documentWith({
        status: "failed",
        pageCount: null,
        errorCode: "password_protected",
        errorDetail: "The PDF requires a password to open",
      }),
      showUploadDate: false,
    });

    await page.getByText("Failed").click();

    await expect.element(page.getByText("This PDF is password-protected.")).toBeVisible();
    await expect.element(page.getByText("Replace with another PDF")).toBeVisible();
    await expect.element(page.getByRole("button", { name: "Delete" })).toBeVisible();
    await expect.element(page.getByRole("button", { name: "Try again" })).not.toBeInTheDocument();
  });

  it("offers a retry when processing failed on our side", async () => {
    render(DocumentRow, {
      document: documentWith({ status: "failed", errorCode: "internal", errorDetail: "timeout" }),
      showUploadDate: false,
    });

    await page.getByText("Failed").click();

    await expect.element(page.getByRole("button", { name: "Try again" })).toBeVisible();
  });

  it("shows the upload date when another document has the same name", async () => {
    render(DocumentRow, { document: documentWith({}), showUploadDate: true });

    await expect.element(page.getByText("uploaded Oct 26, 2026, 12:00 PM UTC")).toBeVisible();
  });
});
