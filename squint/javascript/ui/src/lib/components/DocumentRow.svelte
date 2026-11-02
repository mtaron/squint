<script lang="ts">
  import type { Snippet } from "svelte";
  import type { MouseEventHandler } from "svelte/elements";
  import { page } from "$app/state";
  import { formatBytes } from "#lib/ingest.ts";

  let {
    name,
    href,
    sizeBytes,
    pageCount = null,
    tone,
    title,
    selected = false,
    confirming = false,
    onselect,
    ondelete,
    status,
  }: {
    name: string;
    href?: string;
    sizeBytes: number;
    pageCount?: number | null;
    tone?: "quiet" | "problem";
    title?: string;
    selected?: boolean;
    /** Marks the row as one that's about to be deleted */
    confirming?: boolean;
    onselect?: (range: boolean) => void;
    ondelete?: MouseEventHandler<HTMLButtonElement>;
    /** Spans the row, below the name */
    status?: Snippet;
  } = $props();

  const plural = new Intl.PluralRules("en");
</script>

<li class={["row", tone, { selected, confirming }]} {title}>
  {#if onselect}
    <input
      class="select"
      type="checkbox"
      aria-label="Select {name}"
      checked={selected}
      onclick={(event) => onselect(event.shiftKey)}
    />
  {/if}
  <span class="name">
    {#if href}
      <a class="label" {href}>{name}</a>
    {:else}
      <span class="label">{name}</span>
    {/if}
  </span>
  <span class="details">
    <span class="pages">
      {#if pageCount !== null}
        {pageCount.toLocaleString(page.data.locale)}
        {plural.select(pageCount) === "one" ? "page" : "pages"}
      {/if}
    </span>
    <span class="size">{sizeBytes > 0 ? formatBytes(sizeBytes, page.data.locale) : ""}</span>
  </span>
  {#if ondelete}
    <button class="delete" aria-label="Delete {name}" onclick={ondelete}>
      <span class="i-ph-trash-duotone" aria-hidden="true"></span>
    </button>
  {/if}
  {#if status}
    <div class="status">{@render status()}</div>
  {/if}
</li>

<style>
  /* The list's columns, so names, page counts and sizes line up from row to row */
  .row {
    position: relative;
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: subgrid;
    align-items: baseline;
    row-gap: var(--space-1);
    padding-block: var(--space-2);
    font-size: var(--step-0);
  }

  .select {
    grid-area: 1 / 1;
    position: relative;
    z-index: 1;
    width: 1.125rem;
    height: 1.125rem;
    align-self: center;
    accent-color: var(--ink);
    cursor: pointer;
    opacity: 0;
    transition: opacity 120ms var(--ease-out);

    &:checked {
      opacity: 1;
    }
  }

  :global(.selecting) .select {
    opacity: 1;
  }

  .name {
    grid-area: 1 / 2;
    font-weight: 500;
    overflow-wrap: anywhere;
  }

  /* Marker is spent on what the person is doing, so a finished list stays plain ink */
  .label {
    --swipe-color: var(--marker);
    color: inherit;
    text-decoration: underline 0.25em transparent;
    text-underline-offset: 0.15em;
    text-decoration-skip-ink: none;
    background: linear-gradient(100deg, var(--swipe-color), var(--swipe-color)) no-repeat left
      center / 0% 82%;
    padding-inline: 0.18em;
    margin-inline: -0.18em;
    border-radius: 0.3em 0.6em 0.4em 0.7em / 0.7em 0.35em 0.6em 0.4em;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    transition: background-size 420ms var(--ease-out);
  }

  /* The whole row is the link */
  a.label::after {
    content: "";
    position: absolute;
    inset: 0;
  }

  .selected .label,
  .confirming .label {
    color: var(--on-marker);
    background-size: 100% 82%;
  }

  .confirming .label {
    --swipe-color: var(--marker-pink);
  }

  .details {
    display: contents;
  }

  .pages,
  .size {
    color: var(--ink-soft);
    font-size: var(--step--1);
    text-align: end;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
  }

  .pages {
    grid-area: 1 / 3;
  }

  .size {
    grid-area: 1 / 4;
  }

  .delete {
    grid-area: 1 / -2;
    position: relative;
    z-index: 1;
    display: grid;
    place-items: center;
    align-self: center;
    padding: var(--space-1);
    background: none;
    border: 0;
    border-radius: var(--radius-small);
    color: var(--ink-soft);
    font-size: var(--step-1);
    cursor: pointer;
    opacity: 0;
    transition: opacity 120ms var(--ease-out);

    &:hover {
      color: light-dark(#b0215f, var(--marker-pink));
    }
  }

  .row:focus-within {
    .select,
    .delete {
      opacity: 1;
    }
  }

  .status {
    grid-column: 2 / -1;
    display: flex;
    align-items: center;
    gap: var(--space-4);
    color: var(--ink-soft);
    font-size: var(--step--1);
  }

  .quiet .label {
    color: var(--ink-soft);
  }

  .quiet.selected .label,
  .quiet.confirming .label {
    color: var(--on-marker);
  }

  .problem .status {
    align-items: baseline;
    justify-content: space-between;
    color: light-dark(#b0215f, var(--marker-pink));
  }

  @media (hover: hover) {
    .row:hover {
      a.label {
        text-decoration-color: var(--swipe-color);
      }

      .select,
      .delete {
        opacity: 1;
      }
    }
  }

  @media (hover: none) {
    .select,
    .delete {
      opacity: 1;
    }
  }

  @media (width < 36rem) {
    .details {
      grid-area: 2 / 2;
      display: flex;
      gap: var(--space-4);
    }

    .pages:empty,
    .size:empty {
      display: none;
    }

    .delete {
      grid-area: 1 / -2 / span 2;
    }
  }
</style>
