<script lang="ts">
  import type { Snippet } from "svelte";
  import { formatBytes } from "#lib/ingest.ts";

  let {
    name,
    sizeBytes,
    pageCount = null,
    tone,
    status,
  }: {
    name: string;
    sizeBytes: number;
    pageCount?: number | null;
    tone?: "quiet" | "problem";
    /** Spans the whole row, below the name */
    status?: Snippet;
  } = $props();

  const plural = new Intl.PluralRules("en");
</script>

<li class={["row", tone]}>
  <span class="name">{name}</span>
  <span class="pages">
    {#if pageCount !== null}
      {pageCount.toLocaleString("en")}
      {plural.select(pageCount) === "one" ? "page" : "pages"}
    {/if}
  </span>
  <span class="size">{sizeBytes > 0 ? formatBytes(sizeBytes) : ""}</span>
  {#if status}
    <div class="status">{@render status()}</div>
  {/if}
</li>

<style>
  /* The list's columns, so names, page counts and sizes line up from row to row */
  .row {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: subgrid;
    align-items: baseline;
    row-gap: var(--space-2);
    padding-block: var(--space-3);
    border-bottom: 1px solid var(--rule);
  }

  .name {
    font-weight: 600;
    overflow-wrap: anywhere;
  }

  .pages,
  .size {
    color: var(--ink-soft);
    text-align: end;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
  }

  .status {
    grid-column: 1 / -1;
    display: flex;
    align-items: center;
    gap: var(--space-4);
    color: var(--ink-soft);
  }

  .quiet .name {
    color: var(--ink-soft);
    font-weight: 400;
  }

  .problem .status {
    align-items: baseline;
    justify-content: space-between;
    color: light-dark(#b0215f, var(--marker-pink));
  }
</style>
