<script lang="ts">
  import { resolve } from "$app/paths";
  import DocumentRow from "#lib/components/DocumentRow.svelte";
  import FilePickers from "#lib/components/FilePickers.svelte";
  import type { DocumentIngestion, UploadProgress } from "#lib/ingest.ts";
  import type { QueuedUpload } from "#lib/state/uploads.svelte.ts";

  interface ListedDocument {
    id: string;
    name: string;
    sizeBytes: number;
    pageCount: number | null;
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
    progress,
    statuses,
    formIssues,
    dragging,
    onfiles,
    ondismiss,
  }: {
    documents: ListedDocument[];
    failures: FailedDocument[];
    uploads: QueuedUpload[];
    progress: Record<string, UploadProgress>;
    statuses: Record<string, DocumentIngestion>;
    /** Problems from a post made without JavaScript */
    formIssues: string[];
    dragging: boolean;
    onfiles: (files: File[]) => void;
    ondismiss: (id: string) => void;
  } = $props();

  const uploadTones = { queued: "quiet", uploading: undefined, failed: "problem" } as const;
</script>

<section class={["library", { dragging }]} aria-labelledby="library-heading">
  <header>
    <h1 id="library-heading">Documents</h1>
    <FilePickers size="compact" {onfiles} />
  </header>

  {#if formIssues.length > 0}
    <div class="form-issues" role="alert">
      <ul>
        {#each formIssues as message, index (index)}
          <li>{message}</li>
        {/each}
      </ul>
      <a href="/">Dismiss</a>
    </div>
  {/if}

  <ol>
    {#each uploads as upload (upload.id)}
      <DocumentRow name={upload.name} sizeBytes={upload.size} tone={uploadTones[upload.status]}>
        {#snippet status()}
          {#if upload.status === "queued"}
            Waiting to upload
          {:else if upload.status === "uploading"}
            <span id="uploading-{upload.id}">Uploading</span>
            <progress
              aria-labelledby="uploading-{upload.id}"
              max={upload.size}
              value={progress[upload.id]?.loaded ?? 0}
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
    {#each documents as document (document.id)}
      {@const latest = statuses[document.id]?.latest}
      {@const pageCount = document.pageCount ?? latest?.pageCount ?? null}
      {@const ready = document.pageCount !== null || latest?.state === "ingested"}
      {#snippet preparing()}
        {#if latest?.state === "rasterizing"}
          <span id="preparing-{document.id}">Preparing pages</span>
          <progress
            aria-labelledby="preparing-{document.id}"
            max={latest.pageCount ?? 1}
            value={latest.pagesDone ?? 0}
          ></progress>
        {:else}
          Checking the PDF…
        {/if}
      {/snippet}
      <DocumentRow
        name={document.name}
        href={ready ? resolve("/documents/[id]", { id: document.id }) : undefined}
        sizeBytes={document.sizeBytes}
        {pageCount}
        status={ready ? undefined : preparing}
      />
    {/each}
  </ol>
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

  h1 {
    font-size: clamp(var(--step-3), 4vw, var(--step-4));
  }

  .form-issues {
    display: flex;
    flex-wrap: wrap;
    align-items: start;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-4);
    border-inline-start: 0.25rem solid var(--marker-pink);
    background: var(--surface);
    font-size: var(--step-0);

    ul {
      padding-inline-start: var(--space-4);
    }
  }

  ol {
    display: grid;
    grid-template-columns: 1fr auto auto;
    column-gap: var(--space-5);
    padding: 0;
    list-style: none;
    border-top: 1px solid var(--ink);
  }

  progress {
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
      background: var(--marker);
    }

    &::-moz-progress-bar {
      background: var(--marker);
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
