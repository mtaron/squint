<script lang="ts">
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import PageBoxes from "#lib/components/PageBoxes.svelte";
  import { search } from "#lib/documents.remote.ts";
  import { groupHits, type SearchHit } from "#lib/search.ts";

  let { query, names }: { query: string; names: Map<string, string> } = $props();

  // `current` is undefined on the server, which leaves the search to the browser
  const results = $derived(search({ query }));
  const latest = $derived(results.current);
  // A page from a document deleted since the search started has nowhere to link to
  const pages = $derived((latest?.pages ?? []).filter(({ documentId }) => names.has(documentId)));
  const grouped = $derived(groupHits(pages));
  const reading = $derived(pages.filter(({ boxes }) => boxes == null).length);
  const busy = $derived(!latest || latest.state === "searching" || latest.state === "locating");
  const quoted = $derived(`“${query}”`);

  const summary = $derived.by(() => {
    const state = latest?.state ?? "searching";
    if (state === "failed") {
      return "This search couldn't finish. Try again.";
    }
    if (state === "searching") {
      return `Searching for ${quoted}…`;
    }
    if (state === "locating" && grouped.matches.length === 0) {
      return `Reading the best pages for ${quoted}…`;
    }
    const count = grouped.matches.length.toLocaleString(page.data.locale);
    if (grouped.matches.length === 1) {
      return `${quoted} is on 1 page`;
    }
    if (grouped.matches.length > 1) {
      return `${quoted} is on ${count} pages`;
    }
    return grouped.related.length > 0
      ? `No page shows ${quoted} word for word`
      : `Nothing matches ${quoted}`;
  });

  function hitHref({ documentId, pageNumber }: SearchHit) {
    const viewer = resolve("/documents/[id]", { id: documentId });
    return `${viewer}?${new URLSearchParams({ q: query })}#page=${pageNumber}`;
  }

  function thumbnail({ documentId, pageNumber }: SearchHit) {
    return resolve("/documents/[id]/thumbnails/[page].webp", {
      id: documentId,
      page: String(pageNumber),
    });
  }
</script>

{#snippet hits(list: SearchHit[])}
  <ol class="hits">
    {#each list as hit (`${hit.documentId}-${hit.pageNumber}`)}
      <li>
        <a href={hitHref(hit)}>
          <span class="thumbnail">
            <img src={thumbnail(hit)} alt="" decoding="async" />
            {#if hit.boxes?.length}
              <PageBoxes boxes={hit.boxes} />
            {/if}
          </span>
          <span class="name">{names.get(hit.documentId)}</span>
          <span class="page">Page {hit.pageNumber.toLocaleString(page.data.locale)}</span>
        </a>
      </li>
    {/each}
  </ol>
{/snippet}

<section class="results" aria-labelledby="results-heading" aria-busy={busy}>
  <h2 id="results-heading" aria-live="polite">{summary}</h2>

  {#if grouped.matches.length > 0}
    {@render hits(grouped.matches)}
  {/if}

  {#if grouped.related.length > 0}
    <section aria-labelledby="related-heading">
      <h3 id="related-heading">Related pages</h3>
      <p>These pages are about your search, but don't show it word for word.</p>
      {@render hits(grouped.related)}
    </section>
  {/if}

  {#if reading > 0 && (grouped.matches.length > 0 || grouped.related.length > 0)}
    <p class="reading">
      Reading {reading === 1
        ? "1 more page"
        : `${reading.toLocaleString(page.data.locale)} more pages`}…
    </p>
  {/if}
</section>

<style>
  .results {
    display: grid;
    gap: var(--space-5);
    padding-block-start: var(--space-2);
    border-block-start: 1px solid var(--ink);
  }

  h2 {
    font-size: var(--step-2);
  }

  h3 {
    font-size: var(--step-1);
  }

  section > p,
  .reading {
    color: var(--ink-soft);
  }

  .hits {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
    gap: var(--space-5) var(--space-4);
    margin-block-start: var(--space-3);
    padding: 0;
    list-style: none;
  }

  a {
    display: grid;
    gap: var(--space-1);
    text-decoration: none;

    &:hover .name {
      text-decoration: underline;
    }
  }

  /* Shrinks to the image, so the boxes' percentages are of the page */
  .thumbnail {
    position: relative;
    display: block;
    margin-block-end: var(--space-1);
    background: white;
    box-shadow: 0 0 0 1px var(--rule);
  }

  img {
    display: block;
    width: 100%;
    height: auto;
  }

  .name {
    font-weight: 600;
    overflow-wrap: anywhere;
  }

  .page {
    color: var(--ink-soft);
    font-size: var(--step--1);
    font-variant-numeric: tabular-nums;
  }
</style>
