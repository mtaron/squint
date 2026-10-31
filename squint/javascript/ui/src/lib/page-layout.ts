export interface PageSize {
  width: number;
  height: number;
}

export interface PageLayout {
  /** Where each page starts */
  offsets: number[];
  heights: number[];
  total: number;
}

/** Stacks the pages, each scaled to `width`. Sizes are known up front, so nothing needs measuring. */
export function layOutPages(pages: PageSize[], width: number, gap: number): PageLayout {
  const offsets: number[] = [];
  const heights: number[] = [];
  let position = gap;
  for (const page of pages) {
    const height = (width * page.height) / page.width;
    offsets.push(position);
    heights.push(height);
    position += height + gap;
  }
  return { offsets, heights, total: width > 0 ? position : 0 };
}

/** The last page starting at or above `position`. */
export function pageAt({ offsets }: PageLayout, position: number): number {
  let low = 0;
  let high = offsets.length - 1;
  while (low < high) {
    const middle = Math.ceil((low + high) / 2);
    if (offsets[middle] <= position) {
      low = middle;
    } else {
      high = middle - 1;
    }
  }
  return low;
}

export function visiblePages(
  layout: PageLayout,
  scrollTop: number,
  viewportHeight: number,
  overscan: number,
): { first: number; last: number } | undefined {
  if (layout.total === 0) {
    return undefined;
  }
  return {
    first: Math.max(0, pageAt(layout, scrollTop) - overscan),
    last: Math.min(
      layout.offsets.length - 1,
      pageAt(layout, scrollTop + viewportHeight) + overscan,
    ),
  };
}

const PAGE_HASH = /^#page=([1-9]\d*)$/;

/** The index of the page a `#page=N` URL hash points to, or of the first page if it points nowhere. */
export function pageFromHash(hash: string, pageCount: number): number {
  const pageNumber = PAGE_HASH.exec(hash)?.[1];
  return pageNumber ? Math.min(Number(pageNumber), pageCount) - 1 : 0;
}
