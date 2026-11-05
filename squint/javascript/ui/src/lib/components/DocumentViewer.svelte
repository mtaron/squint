<script lang="ts">
  import { untrack } from "svelte";
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import PageBoxes from "#lib/components/PageBoxes.svelte";
  import PageScroller from "#lib/components/PageScroller.svelte";
  import SearchBar from "#lib/components/SearchBar.svelte";
  import { search } from "#lib/documents.remote.ts";
  import { pageFromHash, type PageSize } from "#lib/page-layout.ts";
  import { groupHits, queryFromUrl } from "#lib/search.ts";

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

  const query = $derived(queryFromUrl(page.url));
  // `current` is undefined on the server, which leaves the search to the browser
  const results = $derived(query ? search({ query, documentId: id }) : undefined);
  const latest = $derived(results?.current);
  const grouped = $derived(groupHits(latest?.pages ?? []));
  const boxes = $derived(
    new Map(grouped.matches.map((hit) => [hit.pageNumber - 1, hit.boxes ?? []])),
  );
  // In reading order, which is how previous and next move through them
  const matchPages = $derived([...boxes.keys()].sort((a, b) => a - b));
  const relatedPages = $derived(
    grouped.related.map(({ pageNumber }) => pageNumber - 1).sort((a, b) => a - b),
  );
  const previousMatch = $derived(matchPages.findLast((index) => index < current));
  const nextMatch = $derived(matchPages.find((index) => index > current));
  const quoted = $derived(`“${query}”`);

  const searchSummary = $derived.by(() => {
    const state = latest?.state ?? "searching";
    if (state === "failed") {
      return "This search couldn't finish. Try again.";
    }
    if (state === "searching") {
      return `Searching for ${quoted}…`;
    }
    if (matchPages.length > 0) {
      const position = matchPages.indexOf(current);
      const count = matchPages.length.toLocaleString(page.data.locale);
      return position === -1
        ? `${quoted} is on ${matchPages.length === 1 ? "1 page" : `${count} pages`}`
        : `Match ${(position + 1).toLocaleString(page.data.locale)} of ${count}`;
    }
    if (state === "locating") {
      return `Reading the best pages for ${quoted}…`;
    }
    return relatedPages.length > 0
      ? `No page shows ${quoted} word for word`
      : `Nothing in this document matches ${quoted}`;
  });

  // The best match the first time one turns up for a search made here. A link to the results
  // names its page already.
  let jumpedFor = "";
  $effect(() => {
    const best = grouped.matches[0];
    if (!best || jumpedFor === query) {
      return;
    }
    jumpedFor = query;
    untrack(() => {
      if (page.state.searched) {
        reader?.scrollToPage(best.pageNumber - 1);
      }
    });
  });
</script>

{#snippet pageLink(index: number, label: string)}
  <a href="#page={index + 1}" onclick={() => reader?.scrollToPage(index)}>{label}</a>
{/snippet}

<div class="viewer">
  <header>
    <h1>{name}</h1>
    <SearchBar label="Search this document" keepHash="#page={current + 1}" />
    <p>
      Page {(current + 1).toLocaleString(page.data.locale)} of
      {pages.length.toLocaleString(page.data.locale)}
    </p>
  </header>

  {#if query}
    <div
      class="search"
      aria-busy={!latest || latest.state === "searching" || latest.state === "locating"}
    >
      <p aria-live="polite">{searchSummary}</p>
      {#if matchPages.length > 0}
        <nav class="matches" aria-label="Matches">
          {#if previousMatch !== undefined}
            {@render pageLink(previousMatch, "Previous")}
          {/if}
          {#if nextMatch !== undefined}
            {@render pageLink(nextMatch, "Next")}
          {/if}
        </nav>
      {/if}
      {#if relatedPages.length > 0}
        <nav class="related" aria-label="Related pages">
          Related:
          {#each relatedPages as index (index)}
            {@render pageLink(index, `p. ${(index + 1).toLocaleString(page.data.locale)}`)}
          {/each}
        </nav>
      {/if}
    </div>
  {/if}

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
          {#if boxes.has(index)}
            <PageBoxes boxes={boxes.get(index) ?? []} />
          {/if}
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
      {#if boxes.has(index)}
        <PageBoxes boxes={boxes.get(index) ?? []} />
      {/if}
    {/snippet}
  </PageScroller>
</div>

<style>
  .viewer {
    display: grid;
    grid-template-columns: 10rem minmax(0, 1fr);
    grid-template-rows: auto auto minmax(0, 1fr);
    height: 100%;
    border-top: 1px solid var(--rule);
  }

  header {
    grid-column: 1 / -1;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
    padding: var(--space-3) var(--gutter);
    border-bottom: 1px solid var(--rule);
  }

  h1 {
    flex: 1;
    font-size: var(--step-1);
    overflow-wrap: anywhere;
  }

  .search {
    grid-column: 1 / -1;
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: var(--space-2) var(--space-4);
    padding: var(--space-2) var(--gutter);
    border-bottom: 1px solid var(--rule);
    background: var(--surface);
    font-variant-numeric: tabular-nums;

    & p {
      font-weight: 600;
    }
  }

  .matches,
  .related {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
  }

  .related {
    color: var(--ink-soft);
  }

  header p {
    flex-shrink: 0;
    color: var(--ink-soft);
    font-size: var(--step-0);
    font-variant-numeric: tabular-nums;
  }

  /* The last row, whether or not the search panel above them is showing */
  .strip,
  .viewer > :global(.pane) {
    grid-row: -2;
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
