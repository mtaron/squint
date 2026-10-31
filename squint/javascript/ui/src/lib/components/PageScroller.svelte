<script lang="ts">
  import { tick, untrack, type Snippet } from "svelte";
  import AfterDelay from "#lib/components/AfterDelay.svelte";
  import { layOutPages, pageAt, visiblePages, type PageSize } from "#lib/page-layout.ts";

  // A page counts as the one being read once it reaches this far down the pane. The top would miss
  // the last pages of a document, the middle would skip past a short landscape page.
  const READING_LINE = 0.25;
  // Browsers finish fetching an image even after it leaves the page, so a page has to stay mounted
  // this long before it renders, or dragging the scrollbar would fetch the whole document
  const RENDER_DELAY_MS = 120;

  let {
    pages,
    label,
    maxPageWidth,
    gap,
    overscan,
    initialPage = 0,
    oncurrent,
    page,
  }: {
    pages: PageSize[];
    label: string;
    maxPageWidth: number;
    gap: number;
    /** How many pages to keep mounted beyond each edge of the pane */
    overscan: number;
    initialPage?: number;
    oncurrent?: (index: number) => void;
    page: Snippet<[index: number]>;
  } = $props();

  let pane = $state<HTMLElement>();
  let paneWidth = $state(0);
  let paneHeight = $state(0);
  let scrollTop = $state(0);

  const pageWidth = $derived(Math.max(0, Math.min(paneWidth - 2 * gap, maxPageWidth)));
  const layout = $derived(layOutPages(pages, pageWidth, gap));
  const range = $derived(visiblePages(layout, scrollTop, paneHeight, overscan));
  const mounted = $derived(
    range
      ? Array.from({ length: range.last - range.first + 1 }, (_, offset) => range.first + offset)
      : [],
  );

  // Where the reader is, so a resize that changes every page's height keeps them there
  let anchor = untrack(() => ({ index: initialPage, fraction: 0 }));

  function trackScroll(event: Event & { currentTarget: HTMLElement }) {
    scrollTop = event.currentTarget.scrollTop;
    const index = pageAt(layout, scrollTop + paneHeight * READING_LINE);
    anchor = {
      index,
      fraction: (scrollTop - layout.offsets[index]) / layout.heights[index],
    };
    oncurrent?.(index);
  }

  // After `tick`, since the browser would clamp the position to the spacer's previous height
  $effect(() => {
    const { offsets, heights, total } = layout;
    if (total > 0) {
      void tick().then(() => {
        if (pane) {
          pane.scrollTop = offsets[anchor.index] + anchor.fraction * heights[anchor.index];
        }
      });
    }
  });

  export function scrollToPage(index: number) {
    anchor = { index, fraction: 0 };
    if (pane) {
      pane.scrollTop = layout.offsets[index];
    }
  }

  /** Scrolls only if the page is out of view, so a reader browsing the pane isn't interrupted. */
  export function reveal(index: number) {
    if (!pane) {
      return;
    }
    const top = layout.offsets[index];
    const height = layout.heights[index];
    if (top < pane.scrollTop || top + height > pane.scrollTop + paneHeight) {
      pane.scrollTop = top - (paneHeight - height) / 2;
    }
  }
</script>

<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
<div
  bind:this={pane}
  bind:clientWidth={paneWidth}
  bind:clientHeight={paneHeight}
  class="pane"
  role="region"
  aria-label={label}
  tabindex="0"
  onscroll={trackScroll}
>
  <div class="spacer" role="list" style:height="{layout.total}px">
    {#each mounted as index (index)}
      <div
        class="page"
        role="listitem"
        aria-posinset={index + 1}
        aria-setsize={pages.length}
        style:top="{layout.offsets[index]}px"
        style:width="{pageWidth}px"
        style:height="{layout.heights[index]}px"
      >
        <AfterDelay ms={RENDER_DELAY_MS}>
          {@render page(index)}
        </AfterDelay>
      </div>
    {/each}
  </div>
</div>

<style>
  /* Strict containment stops the pages it mounts from growing the pane, which would mount more */
  .pane {
    height: 100%;
    overflow-y: auto;
    overscroll-behavior: contain;
    contain: strict;
  }

  .spacer {
    position: relative;
  }

  .page {
    position: absolute;
    left: 50%;
    translate: -50% 0;
    background: white;
    box-shadow: 0 0 0 1px var(--rule);
  }
</style>
