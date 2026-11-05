export const MAX_QUERY_LENGTH = 200;

/** Corners on a 0–1000 scale relative to the page image: Box in squint/python/apps/extract */
export interface Box {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface SearchHit {
  documentId: string;
  pageNumber: number;
  score: number;
  /** Null until Qwen has read the page, and empty when it didn't find the query there. */
  boxes?: Box[] | null;
}

/** Published on the `search` topic of each search workflow's stream, by squint/python/apps/extract. */
export interface SearchEvent {
  state: "searching" | "locating" | "done" | "failed";
  pages: SearchHit[];
}

export function isFinalSearchEvent({ state }: SearchEvent): boolean {
  return state === "done" || state === "failed";
}

/**
 * Pages that show the query, then pages that are about it without showing it, each best first.
 * Pages Qwen is still reading stay out of both.
 */
export function groupHits(pages: SearchHit[]): { matches: SearchHit[]; related: SearchHit[] } {
  return {
    matches: pages.filter(({ boxes }) => boxes && boxes.length > 0),
    related: pages.filter(({ boxes }) => boxes?.length === 0),
  };
}

/** Where a box sits on its page, in percentages of the page's size. */
export function boxPlacement({ x1, y1, x2, y2 }: Box) {
  return {
    left: `${x1 / 10}%`,
    top: `${y1 / 10}%`,
    width: `${(x2 - x1) / 10}%`,
    height: `${(y2 - y1) / 10}%`,
  };
}

/** The query in a search link, or the empty string. */
export function queryFromUrl(url: { searchParams: Pick<URLSearchParams, "get"> }): string {
  return url.searchParams.get("q")?.trim() ?? "";
}
