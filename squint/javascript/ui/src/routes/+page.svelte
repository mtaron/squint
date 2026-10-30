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
    <title>squint: structured data from piles of PDFs</title>
    <meta
      name="description"
      content="squint looks at every page of your PDFs and hands back the fields you asked for, as tidy rows. Self-hosted, vision-first document extraction."
    />
  {/if}
</svelte:head>

{#if data.user}
  <Library />
{:else}
  <Landing />
{/if}
