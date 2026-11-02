<script lang="ts">
  import DocumentList from "#lib/components/DocumentList.svelte";
  import FirstRun from "#lib/components/FirstRun.svelte";
  import { deleteDocuments, getDocuments } from "#lib/documents.remote.ts";
  import { droppedFiles, isFileDrag } from "#lib/drop.ts";
  import { getIngestion } from "#lib/state/ingestion.svelte.ts";

  const ingestion = getIngestion();

  const documentsQuery = getDocuments();
  const initialDocuments = await documentsQuery;
  // `current` changes as soon as the query does, but is always undefined on the server
  const stored = $derived(documentsQuery.current ?? initialDocuments);
  const documents = $derived(
    stored.filter((document) => {
      const state = ingestion.statuses[document.id]?.latest.state;
      return state !== "failed" && state !== "deleted";
    }),
  );
  const firstRun = $derived(
    documents.length === 0 && ingestion.failures.length === 0 && ingestion.queue.items.length === 0,
  );

  // dragenter and dragleave fire for every child element crossed, so count them
  let dragDepth = $state(0);

  async function drop(event: DragEvent) {
    if (!isFileDrag(event) || !event.dataTransfer) {
      return;
    }
    event.preventDefault();
    dragDepth = 0;
    ingestion.upload(await droppedFiles(event.dataTransfer));
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
  <FirstRun dragging={dragDepth > 0} onfiles={(files) => ingestion.upload(files)} />
{:else}
  <DocumentList
    {documents}
    failures={ingestion.failures}
    uploads={ingestion.queue.items}
    statuses={ingestion.statuses}
    dragging={dragDepth > 0}
    onfiles={(files) => ingestion.upload(files)}
    ondismiss={(id) => ingestion.dismiss(id)}
    ondelete={deleteDocuments}
  />
{/if}
