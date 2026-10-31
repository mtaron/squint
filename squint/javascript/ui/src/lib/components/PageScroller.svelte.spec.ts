import { createRawSnippet, type ComponentProps } from "svelte";
import { afterEach, describe, expect, it } from "vitest";
import { page } from "vitest/browser";
import { render } from "vitest-browser-svelte";
import PageScroller from "./PageScroller.svelte";

const squarePages = Array.from({ length: 2000 }, () => ({ width: 100, height: 100 }));

const pageItem = createRawSnippet((index: () => number) => ({
  render: () => `<span data-testid="page">Page ${index() + 1}</span>`,
}));

function renderScroller(props: Partial<ComponentProps<typeof PageScroller>> = {}) {
  const host = document.createElement("div");
  host.style.cssText = "width: 400px; height: 400px";
  document.body.append(host);
  const { component } = render(PageScroller, {
    target: host,
    props: {
      pages: squarePages,
      label: "Pages",
      maxPageWidth: 380,
      gap: 10,
      overscan: 1,
      page: pageItem,
      ...props,
    },
  });
  return { component: component as unknown as PageScroller, host };
}

const mountedPages = () =>
  [...document.querySelectorAll("[data-testid=page]")].map((item) => item.textContent);

describe("PageScroller.svelte", () => {
  afterEach(() => {
    for (const pane of document.querySelectorAll("[role=region]")) {
      pane.parentElement?.remove();
    }
  });

  it("mounts only the pages around the viewport", async () => {
    renderScroller();

    await expect.poll(mountedPages).toEqual(["Page 1", "Page 2", "Page 3"]);
  });

  it("jumps to a page without mounting the ones in between", async () => {
    const { component } = renderScroller();
    await expect.element(page.getByText("Page 1", { exact: true })).toBeInTheDocument();

    component.scrollToPage(1499);

    await expect.element(page.getByText("Page 1500", { exact: true })).toBeInTheDocument();
    expect(mountedPages().length).toBeLessThan(6);
    expect(mountedPages()).not.toContain("Page 1");
  });

  it("opens at the initial page", async () => {
    renderScroller({ initialPage: 41 });

    await expect.element(page.getByText("Page 42", { exact: true })).toBeInTheDocument();
    expect(mountedPages()).not.toContain("Page 1");
  });

  it("doesn't render pages that are scrolled straight past", async () => {
    const rendered = new Set<number>();
    const countingPage = createRawSnippet((index: () => number) => ({
      render: () => {
        rendered.add(index());
        return `<span data-testid="page">Page ${index() + 1}</span>`;
      },
    }));
    const { component } = renderScroller({ page: countingPage });
    await expect.poll(mountedPages).toContain("Page 1");

    for (let index = 100; index < 400; index += 3) {
      component.scrollToPage(index);
      await new Promise(requestAnimationFrame);
    }

    await expect.poll(mountedPages).toContain("Page 398");
    expect(rendered.size).toBeLessThan(12);
  });

  it("reports the page being read", async () => {
    let reported = 0;
    const { component } = renderScroller({ oncurrent: (index: number) => (reported = index) });
    await expect.element(page.getByText("Page 1", { exact: true })).toBeInTheDocument();

    component.scrollToPage(99);

    await expect.poll(() => reported).toBe(99);
  });

  it("keeps the page in view when the pane is resized", async () => {
    const { component, host } = renderScroller();
    await expect.element(page.getByText("Page 1", { exact: true })).toBeInTheDocument();
    component.scrollToPage(99);
    await expect.element(page.getByText("Page 100", { exact: true })).toBeInTheDocument();

    host.style.width = "250px";

    await expect.poll(() => mountedPages()).toContain("Page 100");
    await expect.poll(() => distanceFromPaneTop(host)).toBeLessThan(20);
  });
});

function distanceFromPaneTop(host: HTMLElement): number {
  const pane = host.querySelector("[role=region]") as HTMLElement;
  const item = [...host.querySelectorAll("[data-testid=page]")].find(
    ({ textContent }) => textContent === "Page 100",
  );
  return Math.abs(
    (item?.parentElement?.getBoundingClientRect().top ?? Infinity) -
      pane.getBoundingClientRect().top,
  );
}
