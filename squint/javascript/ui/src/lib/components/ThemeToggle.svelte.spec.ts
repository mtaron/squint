import { page } from "vitest/browser";
import { afterEach, describe, expect, it } from "vitest";
import { render } from "vitest-browser-svelte";
import ThemeToggle from "./ThemeToggle.svelte";

describe("ThemeToggle.svelte", () => {
  afterEach(() => {
    localStorage.removeItem("squint:theme");
    delete document.documentElement.dataset.theme;
  });

  it("stores an explicit preference when toggled away from the system theme", async () => {
    const systemDark = matchMedia("(prefers-color-scheme: dark)").matches;
    const opposite = systemDark ? "light" : "dark";
    render(ThemeToggle);

    await page.getByRole("button", { name: "Dark mode" }).click();

    expect(localStorage.getItem("squint:theme")).toBe(opposite);
    expect(document.documentElement.dataset.theme).toBe(opposite);
  });

  it("returns to following the system when toggled back", async () => {
    render(ThemeToggle);
    const button = page.getByRole("button", { name: "Dark mode" });

    await button.click();
    await button.click();

    expect(localStorage.getItem("squint:theme")).toBe("system");
    expect(document.documentElement.dataset.theme).toBeUndefined();
  });

  it("reflects a stored dark preference as pressed", async () => {
    localStorage.setItem("squint:theme", "dark");
    render(ThemeToggle);

    await expect
      .element(page.getByRole("button", { name: "Dark mode" }))
      .toHaveAttribute("aria-pressed", "true");
  });
});
