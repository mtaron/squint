<script lang="ts">
  import { tick, type Snippet } from "svelte";
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import DocumentRow from "#lib/components/DocumentRow.svelte";
  import FilePickers from "#lib/components/FilePickers.svelte";
  import SearchBar from "#lib/components/SearchBar.svelte";
  import SelectionBar from "#lib/components/SelectionBar.svelte";
  import { type DocumentIngestion, unindexedPages, unindexedPagesMessage } from "#lib/ingest.ts";
  import { DocumentSelection } from "#lib/state/document-selection.svelte.ts";
  import type { QueuedUpload } from "#lib/state/uploads.svelte.ts";
  import { groupByUploadDay, uploadedAtLabel } from "#lib/upload-days.ts";

  interface ListedDocument {
    id: string;
    name: string;
    sizeBytes: number;
    pageCount: number | null;
    uploadedAt: Date;
  }

  interface FailedDocument {
    id: string;
    name: string;
    sizeBytes: number;
    error: string;
  }

  let {
    documents,
    failures,
    uploads,
    statuses,
    dragging,
    onfiles,
    ondismiss,
    ondelete,
    results,
  }: {
    documents: ListedDocument[];
    failures: FailedDocument[];
    uploads: QueuedUpload[];
    statuses: Record<string, DocumentIngestion>;
    dragging: boolean;
    onfiles: (files: File[]) => void;
    ondismiss: (id: string) => void;
    ondelete: (ids: string[]) => Promise<void>;
    /** Search results, which take the place of the list */
    results?: Snippet;
  } = $props();

  const uploadTones = { queued: "quiet", uploading: undefined, failed: "problem" } as const;

  const selection = new DocumentSelection();
  const now = new Date();

  let heading = $state<HTMLElement>();

  let askedToDelete = $state<string[]>([]);
  let askedFrom: HTMLElement | undefined;
  let deleting = $state(false);
  let deleteFailed = $state(false);

  const ids = $derived(documents.map(({ id }) => id));
  const days = $derived(groupByUploadDay(documents, { ...page.data, now }));
  const selected = $derived(selection.within(ids));
  const confirming = $derived.by(() => {
    const listed = new Set(ids);
    return new Set(askedToDelete.filter((id) => listed.has(id)));
  });
  const barMessage = $derived.by(() => {
    if (confirming.size === 0) {
      return `${selected.length.toLocaleString(page.data.locale)} selected`;
    }
    if (deleteFailed) {
      return confirming.size === 1
        ? "This document couldn't be deleted. Try again."
        : "These documents couldn't be deleted. Try again.";
    }
    const [only] = confirming;
    return confirming.size === 1
      ? `Delete ${documents.find(({ id }) => id === only)?.name}?`
      : `Delete ${confirming.size.toLocaleString(page.data.locale)} documents?`;
  });

  function cancelConfirmation() {
    askedToDelete = [];
    deleteFailed = false;
  }

  function selectRow(id: string, range: boolean) {
    cancelConfirmation();
    if (range) {
      selection.toggleRange(id, ids);
    } else {
      selection.toggle(id);
    }
  }

  function selectMany(many: string[], selecting: boolean) {
    cancelConfirmation();
    selection.setAll(many, selecting);
  }

  function clearSelection() {
    cancelConfirmation();
    selection.clear();
  }

  function askToDelete(many: string[], from: HTMLElement) {
    deleteFailed = false;
    askedToDelete = many;
    askedFrom = from;
  }

  async function keep() {
    cancelConfirmation();
    await tick();
    (askedFrom?.isConnected ? askedFrom : heading)?.focus();
  }

  async function confirmDelete() {
    const deleted = [...confirming];
    deleting = true;
    deleteFailed = false;
    try {
      await ondelete(deleted);
      selection.setAll(deleted, false);
      askedToDelete = [];
      heading?.focus();
    } catch (error) {
      console.error("Failed to delete documents", error);
      deleteFailed = true;
    } finally {
      deleting = false;
    }
  }

  function pressEscape(event: KeyboardEvent) {
    if (event.key !== "Escape" || deleting) {
      return;
    }
    if (confirming.size > 0) {
      void keep();
    } else {
      clearSelection();
    }
  }
</script>

<svelte:window onkeydown={pressEscape} />

<section
  class={["library", { dragging, selecting: selected.length > 0 }]}
  aria-labelledby="library-heading"
>
  <header>
    <h1 id="library-heading" tabindex="-1" bind:this={heading}>Documents</h1>
    <div class="actions">
      <SearchBar label="Search all documents" />
      <FilePickers size="compact" {onfiles} />
    </div>
  </header>

  {#if results}
    {@render results()}
  {:else}
    <div class="columns">
      {#if uploads.length > 0 || failures.length > 0}
        <ol class="arriving">
          {#each uploads as upload (upload.id)}
            <DocumentRow
              name={upload.name}
              sizeBytes={upload.size}
              tone={uploadTones[upload.status]}
            >
              {#snippet status()}
                {#if upload.status === "queued"}
                  Waiting to upload
                {:else if upload.status === "uploading"}
                  <span id="uploading-{upload.id}">Uploading</span>
                  <progress
                    aria-labelledby="uploading-{upload.id}"
                    max={upload.size}
                    value={upload.loaded}
                  ></progress>
                {:else}
                  <p role="alert">{upload.problems.join(" ")}</p>
                  <button class="dismiss" onclick={() => ondismiss(upload.id)}>Dismiss</button>
                {/if}
              {/snippet}
            </DocumentRow>
          {/each}
          {#each failures as failure (failure.id)}
            <DocumentRow name={failure.name} sizeBytes={failure.sizeBytes} tone="problem">
              {#snippet status()}
                <p role="alert">{failure.error}</p>
                <button class="dismiss" onclick={() => ondismiss(failure.id)}>Dismiss</button>
              {/snippet}
            </DocumentRow>
          {/each}
        </ol>
      {/if}

      {#each days as day (day.key)}
        {@const dayIds = day.documents.map(({ id }) => id)}
        {@const daySelected = selection.within(dayIds).length}
        <section class="day" aria-labelledby="day-{day.key}">
          <div class="day-heading">
            <input
              class="select-day"
              type="checkbox"
              aria-label="Select all from {day.label}"
              checked={daySelected === dayIds.length}
              indeterminate={daySelected > 0 && daySelected < dayIds.length}
              onclick={() => selectMany(dayIds, daySelected < dayIds.length)}
            />
            <h2 id="day-{day.key}">{day.label}</h2>
          </div>
          <ol>
            {#each day.documents as document (document.id)}
              {@const latest = statuses[document.id]?.latest}
              {@const pageCount = document.pageCount ?? latest?.pageCount ?? null}
              {@const ready =
                document.pageCount !== null ||
                latest?.state === "embedding" ||
                latest?.state === "ingested"}
              {@const working = latest?.state === "rasterizing" || latest?.state === "embedding"}
              {@const unindexed = latest ? unindexedPages(latest) : 0}
              {#snippet preparing()}
                {#if working}
                  Processing…
                  <span class="bars">
                    <progress
                      aria-label="Preparing pages"
                      max={latest?.pageCount ?? 1}
                      value={latest?.pagesDone ?? 0}
                    ></progress>
                    <progress
                      class="embedding"
                      aria-label="Indexing pages"
                      max={latest?.pageCount ?? 1}
                      value={latest?.pagesEmbedded ?? 0}
                    ></progress>
                  </span>
                {:else if unindexed > 0}
                  {unindexedPagesMessage(unindexed, page.data.locale)}
                {:else}
                  Checking the PDF…
                {/if}
              {/snippet}
              <DocumentRow
                name={document.name}
                href={ready ? resolve("/documents/[id]", { id: document.id }) : undefined}
                sizeBytes={document.sizeBytes}
                {pageCount}
                tone={ready ? undefined : "quiet"}
                title={uploadedAtLabel(document.uploadedAt, page.data)}
                selected={selection.has(document.id)}
                confirming={confirming.has(document.id)}
                onselect={(range) => selectRow(document.id, range)}
                ondelete={(event) => askToDelete([document.id], event.currentTarget)}
                status={working || unindexed > 0 || !ready ? preparing : undefined}
              />
            {/each}
          </ol>
        </section>
      {/each}
    </div>

    {#if selected.length > 0 || confirming.size > 0}
      <SelectionBar
        message={barMessage}
        confirming={confirming.size > 0}
        {deleting}
        canSelectAll={selected.length < ids.length}
        onselectall={() => selectMany(ids, true)}
        onclear={clearSelection}
        onkeep={keep}
        ondelete={(button) =>
          confirming.size > 0 ? confirmDelete() : askToDelete(selected, button)}
      />
    {/if}
  {/if}

  <p class="visually-hidden" aria-live="polite">
    {selected.length > 0 || confirming.size > 0 ? barMessage : ""}
  </p>
</section>

<style>
  .library {
    display: grid;
    gap: var(--space-5);
    padding-block-start: var(--space-6);
    border-radius: var(--radius-small);
    outline: 0.375rem dashed transparent;
    outline-offset: var(--space-3);
    transition: outline-color 160ms var(--ease-out);

    &.dragging {
      outline-color: var(--ink);
    }
  }

  header {
    display: flex;
    flex-wrap: wrap;
    align-items: end;
    justify-content: space-between;
    gap: var(--space-4);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-3);
  }

  h1 {
    font-size: clamp(var(--step-3), 4vw, var(--step-4));

    &:focus {
      outline: 0;
      box-shadow: none;
    }
  }

  /* Select, name, pages, size and delete, shared by every day so they line up down the page */
  .columns {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto auto auto;
    gap: var(--space-5) var(--space-4);
  }

  .arriving,
  .day,
  .day-heading,
  .day ol {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: subgrid;
    row-gap: 0;
  }

  ol {
    padding: 0;
    list-style: none;
  }

  .arriving {
    padding-block-start: var(--space-2);
    border-block-start: 1px solid var(--ink);
  }

  .day-heading {
    align-items: baseline;
    margin-block-end: var(--space-1);
    padding-block-end: var(--space-2);
    border-block-end: 1px solid var(--ink);
  }

  h2 {
    grid-column: 2 / -1;
    font-size: var(--step-2);
  }

  .select-day {
    width: 1.125rem;
    height: 1.125rem;
    align-self: center;
    accent-color: var(--ink);
    cursor: pointer;
    opacity: 0;
    transition: opacity 120ms var(--ease-out);

    &:focus-visible,
    &:checked,
    &:indeterminate {
      opacity: 1;
    }
  }

  .selecting .select-day {
    opacity: 1;
  }

  @media (hover: hover) {
    .day-heading:hover .select-day {
      opacity: 1;
    }
  }

  @media (hover: none) {
    .select-day {
      opacity: 1;
    }
  }

  @media (width < 36rem) {
    .columns {
      grid-template-columns: auto minmax(0, 1fr) auto;
    }
  }

  progress {
    --fill: var(--marker);
    flex: 1;
    height: 0.5rem;
    appearance: none;
    border: 0;
    border-radius: 999px;
    background: var(--rule);
    overflow: hidden;

    &::-webkit-progress-bar {
      background: var(--rule);
    }

    &::-webkit-progress-value {
      background: var(--fill);
    }

    &::-moz-progress-bar {
      background: var(--fill);
    }

    &.embedding {
      --fill: var(--marker-pink);
    }
  }

  /* Together they're the height of a single bar, sharing its rounded ends */
  .bars {
    flex: 1;
    display: grid;
    border-radius: 999px;
    overflow: hidden;

    & progress {
      width: 100%;
      height: 0.25rem;
      border-radius: 0;
    }
  }

  .dismiss {
    flex-shrink: 0;
    padding: 0;
    background: none;
    border: 0;
    color: var(--ink);
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 0.2em;
    cursor: pointer;
  }
</style>
