import { page } from "vitest/browser";
import { describe, expect, it } from "vitest";
import { render } from "vitest-browser-svelte";
import HeroDemo from "./HeroDemo.svelte";

describe("HeroDemo.svelte", () => {
  it("lists every highlighted field in the extracted table", async () => {
    const { container } = render(HeroDemo);

    const highlighted = [...container.querySelectorAll("mark")].map((mark) =>
      mark.textContent?.trim(),
    );
    expect(highlighted).toHaveLength(3);

    for (const value of highlighted) {
      await expect.element(page.getByRole("cell", { name: value })).toBeInTheDocument();
    }
  });
});
