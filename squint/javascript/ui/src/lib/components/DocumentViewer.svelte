<script lang="ts">
  import { untrack } from "svelte";
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import PageScroller from "#lib/components/PageScroller.svelte";
  import { pageFromHash, type PageSize } from "#lib/page-layout.ts";

  const MAX_PAGE_WIDTH = 960;
  const PAGE_GAP = 16;
  const THUMBNAIL_WIDTH = 128;
  const THUMBNAIL_GAP = 12;

  let { id, name, pages }: { id: string; name: string; pages: PageSize[] } = $props();

  let reader = $state<PageScroller>();
  let strip = $state<PageScroller>();
  const initialPage = untrack(() => pageFromHash(page.url.hash, pages.length));
  let current = $state(initialPage);

  $effect(() => {
    const index = pageFromHash(page.url.hash, pages.length);
    untrack(() => reader?.scrollToPage(index));
  });

  $effect(() => {
    const index = current;
    untrack(() => strip?.reveal(index));
  });

  const pageParams = (index: number) => ({ id, page: String(index + 1) });
</script>

<div class="viewer">
  <header>
    <h1>{name}</h1>
    <p>Page {(current + 1).toLocaleString("en")} of {pages.length.toLocaleString("en")}</p>
  </header>

  <nav class="strip" aria-label="Page thumbnails">
    <PageScroller
      bind:this={strip}
      {pages}
      label="Page thumbnails"
      maxPageWidth={THUMBNAIL_WIDTH}
      gap={THUMBNAIL_GAP}
      overscan={4}
      {initialPage}
    >
      {#snippet page(index)}
        <a
          class="thumbnail"
          href="#page={index + 1}"
          aria-current={index === current ? "page" : undefined}
          onclick={() => reader?.scrollToPage(index)}
        >
          <img
            src={resolve("/documents/[id]/thumbnails/[page].webp", pageParams(index))}
            alt="Page {index + 1}"
            decoding="async"
          />
        </a>
      {/snippet}
    </PageScroller>
  </nav>

  <PageScroller
    bind:this={reader}
    {pages}
    label="Document pages"
    maxPageWidth={MAX_PAGE_WIDTH}
    gap={PAGE_GAP}
    overscan={1}
    {initialPage}
    oncurrent={(index) => (current = index)}
  >
    {#snippet page(index)}
      <img
        src={resolve("/documents/[id]/pages/[page].jpg", pageParams(index))}
        alt="Page {index + 1}"
        decoding="async"
      />
    {/snippet}
  </PageScroller>
</div>

<style>
  .viewer {
    display: grid;
    grid-template-columns: 10rem minmax(0, 1fr);
    grid-template-rows: auto minmax(0, 1fr);
    height: 100%;
    border-top: 1px solid var(--rule);
  }

  header {
    grid-column: 1 / -1;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: var(--space-4);
    padding: var(--space-3) var(--gutter);
    border-bottom: 1px solid var(--rule);
  }

  h1 {
    font-size: var(--step-1);
    overflow-wrap: anywhere;
  }

  header p {
    flex-shrink: 0;
    color: var(--ink-soft);
    font-size: var(--step-0);
    font-variant-numeric: tabular-nums;
  }

  .strip {
    min-height: 0;
    border-inline-end: 1px solid var(--rule);
  }

  .thumbnail {
    display: block;
    height: 100%;

    &[aria-current="page"] {
      outline: 0.1875rem solid var(--marker);
    }
  }

  img {
    display: block;
    width: 100%;
    height: 100%;
  }

  @media (width < 48rem) {
    .viewer {
      grid-template-columns: minmax(0, 1fr);
    }

    .strip {
      display: none;
    }
  }
</style>
