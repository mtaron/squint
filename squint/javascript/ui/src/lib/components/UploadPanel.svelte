<script lang="ts">
  import Button from "#lib/components/Button.svelte";
  import type { UploadOutcome } from "#lib/uploads/documents.ts";
  import { formatBytes, plural } from "#lib/uploads/format.ts";
  import type { UploadQueue } from "#lib/uploads/uploader.svelte.ts";

  type Props = {
    queue: UploadQueue;
    // The result of an upload posted without JavaScript
    posted?: UploadOutcome;
    message?: string;
  };

  let { queue, posted, message }: Props = $props();

  const scan = $derived(queue.scan);
  const outcome = $derived(scan ? queue.outcome : posted);
  const skipped = $derived([...(scan?.skipped ?? []), ...(outcome?.skipped ?? [])]);
  const pdfCount = $derived(scan?.uploads.filter(({ kind }) => kind === "pdf").length ?? 0);
  const archiveCount = $derived((scan?.uploads.length ?? 0) - pdfCount);

  const selectionSummary = $derived.by(() => {
    const parts = [];
    if (pdfCount > 0) parts.push(plural(pdfCount, "PDF"));
    if (archiveCount > 0) parts.push(plural(archiveCount, "archive"));
    return parts.join(" and ") || "No PDFs";
  });
</script>

{#if scan || outcome || message}
  <section class="panel" aria-live="polite">
    {#if message}
      <p class="error">{message}</p>
    {/if}

    {#if scan}
      <p class="summary">
        <strong>{selectionSummary}</strong>
        {#if scan.skipped.length > 0}
          · {plural(scan.skipped.length, "other file")} left out
        {/if}
        {#if scan.tooLarge.length > 0}
          · {plural(scan.tooLarge.length, "file")} too large
        {/if}
      </p>
    {/if}

    {#if queue.running}
      <progress max={queue.totalBytes} value={queue.sentBytes}></progress>
      <div class="status">
        <span>Uploading {formatBytes(queue.sentBytes)} of {formatBytes(queue.totalBytes)}</span>
        <Button variant="quiet" type="button" onclick={() => queue.cancel()}>Cancel</Button>
      </div>
    {:else if outcome}
      <ul class="results">
        {#if outcome.added.length > 0}
          <li>
            <span class="i-ph-check-circle" aria-hidden="true"></span>
            Added {plural(outcome.added.length, "document")}.
          </li>
        {/if}
        {#if outcome.duplicates.length > 0}
          <li>
            <details>
              <summary>
                {plural(outcome.duplicates.length, "PDF")}
                {outcome.duplicates.length === 1 ? "was" : "were"} already uploaded
              </summary>
              <ul>
                {#each outcome.duplicates as duplicate, index (index)}
                  <li>{duplicate.name} is the same file as {duplicate.existingName}</li>
                {/each}
              </ul>
            </details>
          </li>
        {/if}
        {#if outcome.rejected.length > 0 || scan?.tooLarge.length || queue.failures.length > 0}
          <li class="problem">
            <details open>
              <summary>Some files couldn't be added</summary>
              <ul>
                {#each outcome.rejected as rejected, index (index)}
                  <li><strong>{rejected.name}</strong>: {rejected.reason}</li>
                {/each}
                {#each scan?.tooLarge ?? [] as path (path)}
                  <li><strong>{path}</strong>: too large to upload.</li>
                {/each}
                {#each queue.failures as failure (failure.upload.path)}
                  <li><strong>{failure.upload.path}</strong>: {failure.error}</li>
                {/each}
              </ul>
            </details>
          </li>
        {/if}
        {#if skipped.length > 0}
          <li>
            <details>
              <summary>{plural(skipped.length, "file")} left out because they aren't PDFs</summary>
              <ul>
                {#each skipped as path, index (index)}
                  <li>{path}</li>
                {/each}
              </ul>
            </details>
          </li>
        {/if}
      </ul>
      {#if scan}
        <Button variant="quiet" type="button" onclick={() => queue.clear()}>Dismiss</Button>
      {/if}
    {/if}
  </section>
{/if}

<style>
  .panel {
    display: grid;
    gap: var(--space-3);
    justify-items: start;
    width: min(100%, 40rem);
    padding: var(--space-4) var(--space-5);
    background: var(--surface);
    border: 1px solid var(--rule);
    border-radius: var(--radius-small);
    font-size: var(--step-0);
    text-align: start;
  }

  progress {
    width: 100%;
    height: 0.5rem;
    accent-color: var(--ink);
  }

  .status {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    width: 100%;
    color: var(--ink-soft);
  }

  .results {
    display: grid;
    gap: var(--space-2);
    padding: 0;
    list-style: none;

    ul {
      margin-block-start: var(--space-2);
      color: var(--ink-soft);
    }
  }

  summary {
    cursor: pointer;
  }

  .problem summary,
  .error {
    color: var(--danger);
    font-weight: 600;
  }
</style>
