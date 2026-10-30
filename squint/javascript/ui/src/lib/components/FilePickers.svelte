<script lang="ts">
  import { onMount } from "svelte";
  import { uploadDocuments } from "#lib/documents.remote.ts";

  let {
    size = "large",
    onfiles,
  }: { size?: "large" | "compact"; onfiles: (files: File[]) => void } = $props();

  const { files } = uploadDocuments.fields;

  // Without JavaScript the inputs stay visible and the form posts all the chosen files at once
  let enhanced = $state(false);
  onMount(() => {
    enhanced = true;
  });

  function choose(event: Event & { currentTarget: HTMLInputElement }) {
    const input = event.currentTarget;
    onfiles([...(input.files ?? [])]);
    input.value = "";
  }
</script>

<form {...uploadDocuments} enctype="multipart/form-data" class={["pickers", size, { enhanced }]}>
  <label class="button hero">
    <span class="i-ph-folder-open-duotone" aria-hidden="true"></span>
    Choose a folder
    <input {...files.as("file multiple")} webkitdirectory onchange={choose} />
  </label>
  <label class="button quiet">
    <span class="i-ph-file-pdf-duotone" aria-hidden="true"></span>
    Choose a PDF
    <input {...files.as("file multiple")} accept="application/pdf,.pdf" onchange={choose} />
  </label>
  {#if !enhanced}
    <button class="button submit">Upload</button>
  {/if}
</form>

<style>
  .pickers {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: var(--space-4);
  }

  .large .button {
    padding: var(--space-4) var(--space-6);
    font-size: var(--step-1);
  }

  .large .hero {
    padding-inline: var(--space-7);
    font-size: var(--step-2);
  }

  .compact {
    justify-content: start;
    gap: var(--space-2);
  }

  .compact .button {
    padding: var(--space-2) var(--space-4);
  }

  label {
    flex-wrap: wrap;
    justify-content: center;

    &:has(:focus-visible) {
      outline: 2px solid var(--ink);
      outline-offset: 3px;
      box-shadow: 0 0 0 6px var(--marker);
    }
  }

  [class^="i-ph"] {
    font-size: 1.4em;
  }

  input {
    flex-basis: 100%;
    font-size: var(--step--1);
    font-weight: 400;
  }

  .enhanced input {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
  }
</style>
