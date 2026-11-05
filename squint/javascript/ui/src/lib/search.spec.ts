import { expect, test } from "vitest";
import {
  boxPlacement,
  groupHits,
  isFinalSearchEvent,
  queryFromUrl,
  type SearchHit,
} from "./search.ts";

const box = { x1: 100, y1: 250, x2: 400, y2: 275 };

function hit(pageNumber: number, boxes?: SearchHit["boxes"]): SearchHit {
  return { documentId: "V3kQ9xTz2m", pageNumber, score: 1, boxes };
}

test("lists pages that show the query before related ones, leaving out those still being read", () => {
  const pages = [hit(1, []), hit(2, [box]), hit(3, null), hit(4), hit(5, [box, box])];

  const { matches, related } = groupHits(pages);

  expect(matches.map(({ pageNumber }) => pageNumber)).toEqual([2, 5]);
  expect(related.map(({ pageNumber }) => pageNumber)).toEqual([1]);
});

test("places a box in percentages of its page", () => {
  expect(boxPlacement(box)).toEqual({ left: "10%", top: "25%", width: "30%", height: "2.5%" });
});

test("only done and failed end a search", () => {
  expect(isFinalSearchEvent({ state: "searching", pages: [] })).toBe(false);
  expect(isFinalSearchEvent({ state: "locating", pages: [] })).toBe(false);
  expect(isFinalSearchEvent({ state: "done", pages: [] })).toBe(true);
  expect(isFinalSearchEvent({ state: "failed", pages: [] })).toBe(true);
});

test("reads the query from a search link", () => {
  expect(queryFromUrl(new URL("https://squint.loc/documents?q=%20net%20revenue%20"))).toBe(
    "net revenue",
  );
  expect(queryFromUrl(new URL("https://squint.loc/documents"))).toBe("");
});
