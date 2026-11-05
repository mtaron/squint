import { afterEach, describe, expect, it } from "vitest";
import { render } from "vitest-browser-svelte";
import PageBoxes from "./PageBoxes.svelte";

describe("PageBoxes.svelte", () => {
  afterEach(() => {
    document.body.replaceChildren();
  });

  it("covers each box's share of the page", async () => {
    const host = document.createElement("div");
    host.style.cssText = "position: relative; width: 500px; height: 800px";
    document.body.append(host);

    render(PageBoxes, {
      target: host,
      props: {
        boxes: [
          { x1: 100, y1: 250, x2: 400, y2: 275 },
          { x1: 0, y1: 0, x2: 1000, y2: 1000 },
        ],
      },
    });

    const placed = [...host.querySelectorAll<HTMLElement>("[data-testid=search-box]")].map(
      (box) => {
        const { left, top, width, height } = box.getBoundingClientRect();
        const page = host.getBoundingClientRect();
        return [left - page.left, top - page.top, width, height];
      },
    );
    expect(placed).toEqual([
      [50, 200, 150, 20],
      [0, 0, 500, 800],
    ]);
  });
});
