import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { page as browser, userEvent } from "vitest/browser";
import { render } from "vitest-browser-svelte";
import SearchBar from "./SearchBar.svelte";

const app = vi.hoisted(() => ({
  goto: vi.fn(),
  page: { url: new URL("https://squint.loc/documents/V3kQ9xTz2m") },
}));

vi.mock("$app/navigation", () => ({ goto: app.goto }));
vi.mock("$app/state", () => ({ page: app.page }));

function open(url: string, keepHash?: string) {
  app.page.url = new URL(url);
  render(SearchBar, { label: "Search this document", keepHash });
  return browser.getByRole("searchbox", { name: "Search this document" });
}

describe("SearchBar.svelte", () => {
  beforeEach(() => {
    app.goto.mockClear();
  });

  afterEach(() => {
    document.body.replaceChildren();
  });

  it("searches for what was typed, staying on the reader's page", async () => {
    const input = open("https://squint.loc/documents/V3kQ9xTz2m#page=2", "#page=4");

    await input.fill("  net revenue ");
    await userEvent.keyboard("{Enter}");

    expect(app.goto).toHaveBeenCalledWith("/documents/V3kQ9xTz2m?q=net+revenue#page=4", {
      reset: false,
      state: { searched: true },
    });
  });

  it("shows the query it was opened with, and doesn't repeat it", async () => {
    const input = open("https://squint.loc/documents?q=net+revenue");

    await expect.element(input).toHaveValue("net revenue");
    await input.click();
    await userEvent.keyboard("{Enter}");

    expect(app.goto).not.toHaveBeenCalled();
  });

  it("clears the search with Escape without letting the page see the key", async () => {
    const input = open("https://squint.loc/documents?q=net+revenue");
    const pressed = vi.fn();
    window.addEventListener("keydown", pressed);

    await input.click();
    await userEvent.keyboard("{Escape}");
    window.removeEventListener("keydown", pressed);

    await expect.element(input).toHaveValue("");
    expect(app.goto).toHaveBeenCalledWith("/documents", {
      reset: false,
      state: { searched: false },
    });
    expect(pressed).not.toHaveBeenCalled();
  });
});
