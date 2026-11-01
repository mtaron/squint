<script lang="ts">
  import { resolve } from "$app/paths";
  import DocumentViewer from "#lib/components/DocumentViewer.svelte";
  import { getDocumentPages } from "#lib/documents.remote.ts";
  import type { PageProps } from "./$types";

  let { params }: PageProps = $props();

  const document = $derived(await getDocumentPages(params.id));
</script>

<svelte:head>
  <title>squint: {document.name}</title>
</svelte:head>

{#if document.ready}
  <DocumentViewer id={params.id} name={document.name} pages={document.pages} />
{:else}
  <section class="preparing">
    <h1>{document.name}</h1>
    <p>
      Its pages are still being prepared.
      <a href={resolve("/documents")}>Back to your documents</a>
    </p>
  </section>
{/if}

<style>
  .preparing {
    padding: var(--space-6) var(--gutter);
  }
</style>
