<script lang="ts">
  import { SvelteSet } from "svelte/reactivity";
  import DocumentList from "#lib/components/DocumentList.svelte";
  import FirstRun from "#lib/components/FirstRun.svelte";
  import UploadForm from "#lib/components/UploadForm.svelte";
  import {
    getDocuments,
    ingestStatus,
    uploadDocuments,
    uploadProgress,
  } from "#lib/documents.remote.ts";
  import { droppedFiles, isFileDrag } from "#lib/drop.ts";
  import { ingestErrorMessage } from "#lib/ingest.ts";
  import { retriedBy, UploadQueue } from "#lib/state/uploads.svelte.ts";

  const queue = new UploadQueue();
  const progress = uploadProgress();
  const ingestion = ingestStatus();

  const stored = $derived(await getDocuments());
  const statuses = $derived(ingestion.current ?? {});

  // A document that fails ingestion is deleted, so its row comes from its status until dismissed
  const dismissed = new SvelteSet<string>();
  const failures = $derived(
    Object.entries(statuses)
      .filter(([id, { latest }]) => latest.state === "failed" && !dismissed.has(id))
      .map(([id, { name, sizeBytes, latest }]) => ({
        id,
        name,
        sizeBytes,
        error: ingestErrorMessage(latest.error),
      })),
  );
  const documents = $derived(
    stored.filter((document) => statuses[document.id]?.latest.state !== "failed"),
  );
  const formIssues = $derived(
    uploadDocuments.fields.allIssues()?.map((issue) => issue.message) ?? [],
  );
  const firstRun = $derived(
    documents.length === 0 &&
      failures.length === 0 &&
      queue.items.length === 0 &&
      formIssues.length === 0,
  );

  // dragenter and dragleave fire for every child element crossed, so count them
  let dragDepth = $state(0);

  function dismiss(id: string) {
    queue.dismiss(id);
    dismissed.add(id);
  }

  function upload(files: File[]) {
    for (const { id } of retriedBy(failures, files)) {
      dismissed.add(id);
    }
    queue.add(files);
  }

  async function drop(event: DragEvent) {
    if (!isFileDrag(event) || !event.dataTransfer) {
      return;
    }
    event.preventDefault();
    dragDepth = 0;
    upload(await droppedFiles(event.dataTransfer));
  }
</script>

<svelte:window
  ondragenter={(event) => {
    if (isFileDrag(event)) dragDepth += 1;
  }}
  ondragleave={(event) => {
    if (isFileDrag(event)) dragDepth = Math.max(0, dragDepth - 1);
  }}
  ondragover={(event) => {
    if (isFileDrag(event)) event.preventDefault();
  }}
  ondrop={drop}
/>

{#if firstRun}
  <FirstRun dragging={dragDepth > 0} onfiles={upload} />
{:else}
  <DocumentList
    {documents}
    {failures}
    uploads={queue.items}
    progress={progress.current ?? {}}
    {statuses}
    {formIssues}
    dragging={dragDepth > 0}
    onfiles={upload}
    ondismiss={dismiss}
  />
{/if}

{#each queue.uploading as upload (upload.id)}
  <UploadForm {upload} onsettled={(problems) => queue.settle(upload.id, problems)} />
{/each}
