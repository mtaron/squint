<script lang="ts">
  import type { Snippet } from "svelte";
  import Button from "#lib/components/Button.svelte";
  import { MAX_PDF_BYTES } from "#lib/uploads/limits.ts";
  import { formatBytes } from "#lib/uploads/format.ts";
  import {
    dropSelection,
    inputSelection,
    scanSelection,
    type SelectedFile,
  } from "#lib/uploads/scan.ts";
  import type { UploadQueue } from "#lib/uploads/uploader.svelte.ts";

  type Props = { variant: "first-run" | "compact"; queue: UploadQueue; children?: Snippet };

  let { variant, queue, children }: Props = $props();

  // dragenter and dragleave fire for every child element the pointer crosses
  let dragDepth = $state(0);
  const dragging = $derived(dragDepth > 0);

  const accept = ".pdf,.zip,.tar,.tgz,.gz,application/pdf,application/zip";

  function upload(selection: SelectedFile[]) {
    if (selection.length > 0) queue.start(scanSelection(selection));
  }

  function choose(event: Event & { currentTarget: HTMLInputElement }) {
    const input = event.currentTarget;
    if (input.files) upload(inputSelection(input.files));
    input.value = "";
  }

  function hasFiles(event: DragEvent) {
    return event.dataTransfer?.types.includes("Files") ?? false;
  }

  async function drop(event: DragEvent) {
    event.preventDefault();
    dragDepth = 0;
    if (event.dataTransfer) upload(await dropSelection(event.dataTransfer.items));
  }
</script>

<form
  class={["dropzone", variant, { dragging }]}
  method="POST"
  action="?/upload"
  enctype="multipart/form-data"
  onsubmit={(event) => event.preventDefault()}
  ondragenter={(event) => {
    if (hasFiles(event)) dragDepth++;
  }}
  ondragleave={(event) => {
    if (hasFiles(event)) dragDepth = Math.max(0, dragDepth - 1);
  }}
  ondragover={(event) => {
    if (hasFiles(event)) event.preventDefault();
  }}
  ondrop={drop}
>
  <span class="icon i-ph-files-duotone" aria-hidden="true"></span>
  <div class="instructions">
    {#if variant === "first-run"}
      <h1>Drop your PDFs here</h1>
      <p>
        Drag in a PDF, a folder, or a <code>.zip</code> or <code>.tar.gz</code> archive. squint keeps
        the PDFs and leaves everything else out.
      </p>
    {:else}
      <h2>Add more PDFs</h2>
      <p>Drop files, a folder, or an archive here.</p>
    {/if}
  </div>

  <div class="actions">
    <Button as="label">
      <span class="i-ph-file-arrow-up" aria-hidden="true"></span>
      Choose files
      <input class="visually-hidden" type="file" name="files" multiple {accept} onchange={choose} />
    </Button>
    <Button as="label" variant="quiet">
      <span class="i-ph-folder-open" aria-hidden="true"></span>
      Choose a folder
      <input
        class="visually-hidden"
        type="file"
        name="files"
        multiple
        webkitdirectory
        onchange={choose}
      />
    </Button>
    <noscript>
      <Button>Upload</Button>
    </noscript>
  </div>

  {#if variant === "first-run"}
    <p class="limits">Up to {formatBytes(MAX_PDF_BYTES)} and 2,000 pages per PDF.</p>
  {/if}

  {@render children?.()}
</form>

<style>
  .dropzone {
    display: grid;
    justify-items: center;
    align-content: center;
    gap: var(--space-5);
    padding: var(--space-7) var(--space-5);
    border: 4px dashed color-mix(in oklab, var(--ink-soft) 45%, transparent);
    border-radius: 2rem;
    text-align: center;
    transition:
      border-color 160ms var(--ease-out),
      background-color 160ms var(--ease-out);

    &.dragging {
      border-color: var(--ink);
      background: var(--surface);
    }
  }

  .first-run {
    min-height: min(36rem, 70dvh);
    margin-block-start: var(--space-6);

    .icon {
      font-size: var(--step-6);
    }

    .instructions p {
      max-width: 34em;
      color: var(--ink-soft);
      font-size: var(--step-2);
      line-height: 1.45;
    }
  }

  .compact {
    grid-template-columns: auto 1fr auto;
    justify-items: start;
    gap: var(--space-4);
    padding: var(--space-4) var(--space-5);
    border-width: 3px;
    border-radius: 1.25rem;
    text-align: start;

    .icon {
      font-size: var(--step-4);
    }

    h2 {
      font-size: var(--step-2);
    }

    .instructions p {
      color: var(--ink-soft);
      font-size: var(--step-0);
    }

    > :global(:last-child:not(.actions)) {
      grid-column: 1 / -1;
      justify-self: stretch;
    }

    @media (max-width: 40rem) {
      grid-template-columns: 1fr;

      .icon {
        display: none;
      }
    }
  }

  .instructions {
    display: grid;
    gap: var(--space-3);
    justify-items: inherit;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--space-3);
  }

  .limits {
    color: var(--ink-soft);
    font-size: var(--step--1);
  }

  code {
    font-size: 0.9em;
  }
</style>
