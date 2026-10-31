import { describe, expect, test } from "vitest";
import { layOutPages, pageAt, pageFromHash, visiblePages } from "./page-layout.ts";

const PAGES = [
  { width: 100, height: 200 },
  { width: 100, height: 100 },
  { width: 200, height: 100 },
];

describe("layOutPages", () => {
  test("stacks pages scaled to the width, with a gap between them", () => {
    const layout = layOutPages(PAGES, 50, 10);

    expect(layout.heights).toEqual([100, 50, 25]);
    expect(layout.offsets).toEqual([10, 120, 180]);
    expect(layout.total).toBe(215);
  });

  test("has no extent before the width is known", () => {
    expect(layOutPages(PAGES, 0, 10).total).toBe(0);
  });
});

describe("pageAt", () => {
  const layout = layOutPages(PAGES, 50, 10);

  test("finds the page containing a position", () => {
    expect(pageAt(layout, 10)).toBe(0);
    expect(pageAt(layout, 119)).toBe(0);
    expect(pageAt(layout, 120)).toBe(1);
    expect(pageAt(layout, 500)).toBe(2);
  });

  test("treats the space above the first page as the first page", () => {
    expect(pageAt(layout, 0)).toBe(0);
  });
});

describe("visiblePages", () => {
  const manyPages = Array.from({ length: 2000 }, () => ({ width: 100, height: 100 }));
  const layout = layOutPages(manyPages, 100, 0);

  test("includes pages overlapping the viewport and the overscan", () => {
    expect(visiblePages(layout, 1050, 200, 1)).toEqual({ first: 9, last: 13 });
  });

  test("stops at the ends of the document", () => {
    expect(visiblePages(layout, 0, 100, 2)).toEqual({ first: 0, last: 3 });
    expect(visiblePages(layout, 199_950, 100, 2)).toEqual({ first: 1997, last: 1999 });
  });

  test("shows nothing before the pane has a size", () => {
    expect(visiblePages(layOutPages(manyPages, 0, 0), 0, 0, 2)).toBeUndefined();
  });
});

describe("pageFromHash", () => {
  test("reads a one-based page number as an index", () => {
    expect(pageFromHash("#page=12", 20)).toBe(11);
  });

  test("clamps to the last page", () => {
    expect(pageFromHash("#page=99", 20)).toBe(19);
  });

  test.each(["", "#", "#page=", "#page=0", "#page=abc", "#other=3"])("ignores %j", (hash) => {
    expect(pageFromHash(hash, 20)).toBe(0);
  });
});
