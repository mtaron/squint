<script lang="ts">
  import DocumentList from "#lib/components/DocumentList.svelte";
  import DropZone from "#lib/components/DropZone.svelte";
  import Landing from "#lib/components/Landing.svelte";
  import UploadPanel from "#lib/components/UploadPanel.svelte";
  import { refreshDocuments } from "#lib/uploads/refresh.ts";
  import { UploadQueue } from "#lib/uploads/uploader.svelte.ts";
  import type { PageProps } from "./$types";

  let { data, form }: PageProps = $props();

  // Lives here rather than in the drop zone, which is replaced once the first document arrives
  const queue = new UploadQueue("?/upload", refreshDocuments);

  const posted = $derived(form && "outcome" in form ? form.outcome : undefined);
  const message = $derived(form && "message" in form ? form.message : undefined);
  const processing = $derived(
    data.documents?.some(({ status }) => status === "processing") ?? false,
  );

  // Postgres holds the status, so each event just reloads the list. Reloading when the stream
  // (re)connects covers anything that changed while it was disconnected.
  $effect(() => {
    if (!processing) return;
    const events = new EventSource("/api/documents/events");
    events.onopen = refreshDocuments;
    events.onmessage = refreshDocuments;
    return () => events.close();
  });
</script>

<svelte:head>
  {#if data.documents === null}
    <title>squint: structured data from piles of PDFs</title>
    <meta
      name="description"
      content="squint looks at every page of your PDFs and hands back the fields you asked for, as tidy rows. Self-hosted, vision-first document extraction."
    />
  {:else}
    <title>Your documents · squint</title>
  {/if}
</svelte:head>

{#if data.documents === null}
  <Landing />
{:else if data.documents.length === 0}
  <DropZone variant="first-run" {queue}>
    <UploadPanel {queue} {posted} {message} />
  </DropZone>
{:else}
  <div class="library">
    <h1>Your documents</h1>
    <DropZone variant="compact" {queue}>
      <UploadPanel {queue} {posted} {message} />
    </DropZone>
    <DocumentList documents={data.documents} />
  </div>
{/if}

<style>
  .library {
    display: grid;
    gap: var(--space-6);
    padding-block-start: var(--space-6);
  }

  h1 {
    font-size: var(--step-5);
  }
</style>
