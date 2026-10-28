import { randomUUID } from "node:crypto";
import { expect, test, type Page } from "@playwright/test";

// A one-page PDF; PDFium rebuilds the missing cross-reference table
function pdf(label: string): Buffer {
  return Buffer.from(
    [
      "%PDF-1.4",
      "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
      "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
      "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj",
      `% ${label}`,
      "trailer << /Root 1 0 R >>",
      "%%EOF",
    ].join("\n"),
  );
}

async function signUp(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email").fill(`e2e-${randomUUID()}@squint.test`);
  await page.getByLabel("Password").fill(`password-${randomUUID()}`);
  await page.getByLabel("Name").fill("E2E");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page.getByRole("heading", { name: "Drop your PDFs here" })).toBeVisible();
  // The file inputs only upload on change once the page has hydrated
  await page.waitForLoadState("networkidle");
}

test("uploading a PDF replaces the first-run page with the document, which becomes ready", async ({
  page,
}) => {
  await signUp(page);

  await page.getByLabel("Choose files").setInputFiles({
    name: "first.pdf",
    mimeType: "application/pdf",
    buffer: pdf(randomUUID()),
  });

  await expect(page.getByRole("heading", { name: "Your documents" })).toBeVisible();
  const row = page.getByRole("listitem").filter({ hasText: "first.pdf" });
  await expect(row.getByText("Ready")).toBeVisible({ timeout: 60_000 });
  await expect(row.getByText("1 page")).toBeVisible();
});

test.describe("without JavaScript", () => {
  test.use({ javaScriptEnabled: false });

  test("uploads a PDF with the plain form", async ({ page }) => {
    await signUp(page);

    await page.getByLabel("Choose files").setInputFiles({
      name: "plain.pdf",
      mimeType: "application/pdf",
      buffer: pdf(randomUUID()),
    });
    await page.getByRole("button", { name: "Upload" }).click();

    await expect(page.getByText("Added 1 document.")).toBeVisible();
    const row = page.getByRole("listitem").filter({ hasText: "plain.pdf" });
    await expect(async () => {
      await page.goto("/");
      await expect(row.getByText("Ready")).toBeVisible({ timeout: 1000 });
    }).toPass({ timeout: 60_000 });
  });
});
