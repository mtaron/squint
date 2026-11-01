<script lang="ts">
  import { afterNavigate, goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import DocumentList from "#lib/components/DocumentList.svelte";
  import FirstRun from "#lib/components/FirstRun.svelte";
  import { getDocuments } from "#lib/documents.remote.ts";
  import { droppedFiles, isFileDrag } from "#lib/drop.ts";
  import { getIngestion } from "#lib/state/ingestion.svelte.ts";

  const ingestion = getIngestion();

  afterNavigate(syncRoute);

  const stored = $derived(await getDocuments());
  const documents = $derived(
    stored.filter((document) => ingestion.statuses[document.id]?.latest.state !== "failed"),
  );
  const firstRun = $derived(
    documents.length === 0 && ingestion.failures.length === 0 && ingestion.queue.items.length === 0,
  );
  // An upload leaves the queue just before its document reaches `stored`
  const showFirstRun = $derived(firstRun && page.route.id === "/");

  // dragenter and dragleave fire for every child element crossed, so count them
  let dragDepth = $state(0);

  function syncRoute() {
    const route = resolve(firstRun ? "/" : "/documents");
    if (page.url.pathname !== route) {
      void goto(route, { replace: true });
    }
  }

  function dismiss(id: string) {
    ingestion.dismiss(id);
    syncRoute();
  }

  function upload(files: File[]) {
    ingestion.upload(files);
    syncRoute();
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

{#if showFirstRun}
  <FirstRun dragging={dragDepth > 0} onfiles={upload} />
{:else}
  <DocumentList
    {documents}
    failures={ingestion.failures}
    uploads={ingestion.queue.items}
    statuses={ingestion.statuses}
    dragging={dragDepth > 0}
    onfiles={upload}
    ondismiss={dismiss}
  />
{/if}
