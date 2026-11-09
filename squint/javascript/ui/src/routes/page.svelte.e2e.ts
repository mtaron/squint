import { expect, test } from "@playwright/test";

test("sign in links to the login page", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
});

test("the document list asks visitors to sign in", async ({ page }) => {
  await page.goto("/documents");
  await expect(page).toHaveURL(/\/login$/);
});
