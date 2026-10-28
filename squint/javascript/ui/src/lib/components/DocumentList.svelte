<script lang="ts">
  import { enhance } from "$app/forms";
  import { page } from "$app/state";
  import Button from "#lib/components/Button.svelte";
  import DocumentRow from "#lib/components/DocumentRow.svelte";
  import type { DocumentSummary } from "#lib/uploads/documents.ts";
  import { plural } from "#lib/uploads/format.ts";

  let { documents }: { documents: DocumentSummary[] } = $props();

  const onlyFailed = $derived(page.url.searchParams.get("show") === "failed");
  const failed = $derived(documents.filter(({ status }) => status === "failed"));
  const shown = $derived(onlyFailed ? failed : documents);

  const repeatedNames = $derived(
    new Set(
      Object.entries(Object.groupBy(documents, ({ name }) => name))
        .filter(([, named]) => named && named.length > 1)
        .map(([name]) => name),
    ),
  );
</script>

<section aria-labelledby="documents-heading">
  <div class="toolbar">
    <h2 id="documents-heading">{plural(documents.length, "document")}</h2>
    {#if failed.length > 0}
      <span class="failed">{failed.length} failed</span>
      <div class="actions">
        {#if onlyFailed}
          <a href="?">Show all</a>
        {:else}
          <a href="?show=failed">Show only failed</a>
        {/if}
        <form
          method="POST"
          action="?/deleteFailed"
          use:enhance={({ cancel }) => {
            if (!confirm(`Delete ${plural(failed.length, "failed document")}?`)) cancel();
          }}
        >
          <Button variant="quiet">Delete all failed</Button>
        </form>
      </div>
    {/if}
  </div>

  <ul>
    {#each shown as document (document.id)}
      <DocumentRow {document} showUploadDate={repeatedNames.has(document.name)} />
    {/each}
  </ul>
</section>

<style>
  section {
    display: grid;
    gap: var(--space-4);
  }

  .toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: var(--space-3) var(--space-4);
  }

  h2 {
    font-size: var(--step-3);
  }

  .failed {
    color: var(--danger);
    font-size: var(--step-0);
    font-weight: 600;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-4);
    margin-inline-start: auto;
    font-size: var(--step-0);
  }

  ul {
    padding: 0;
    list-style: none;
    border-top: 1px solid var(--rule);
  }
</style>
