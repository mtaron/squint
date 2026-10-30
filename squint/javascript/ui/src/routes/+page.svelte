<script lang="ts">
  import Landing from "#lib/components/Landing.svelte";
  import Library from "#lib/components/Library.svelte";
  import type { PageProps } from "./$types";

  let { data }: PageProps = $props();
</script>

<svelte:head>
  {#if data.user}
    <title>squint: documents</title>
  {:else}
    <title>squint: structured data from your documents</title>
    <meta
      name="description"
      content="squint applies a schema across your documents and shows where on the page each value came from. Vision-first and self-hostable."
    />
  {/if}
</svelte:head>

{#if data.user}
  <Library />
{:else}
  <Landing />
{/if}
