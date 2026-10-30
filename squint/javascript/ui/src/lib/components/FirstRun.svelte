<script lang="ts">
  import FilePickers from "#lib/components/FilePickers.svelte";

  let { dragging, onfiles }: { dragging: boolean; onfiles: (files: File[]) => void } = $props();
</script>

<section class={["drop-zone", { dragging }]} aria-labelledby="first-run-heading">
  <span class="i-ph-files-duotone" aria-hidden="true"></span>
  <h1 id="first-run-heading">Drop a folder of PDFs here</h1>
  <p>
    Drag in a whole folder or a single PDF, or choose one from your computer. Each PDF can be up to
    500 MB and 2,000 pages.
  </p>
  <FilePickers {onfiles} />
</section>

<style>
  .drop-zone {
    display: grid;
    place-content: center;
    justify-items: center;
    gap: var(--space-5);
    min-height: max(28rem, 70dvh);
    margin-block-start: var(--space-4);
    padding: var(--space-7) var(--space-5);
    text-align: center;
    border: 0.375rem dashed var(--rule);
    border-radius: 2.5rem;
    transition:
      border-color 160ms var(--ease-out),
      background-color 160ms var(--ease-out);

    &.dragging {
      border-color: var(--ink);
      background: color-mix(in oklab, var(--marker) 35%, transparent);
    }
  }

  [class^="i-ph"] {
    font-size: var(--step-5);
    color: var(--ink-soft);
  }

  h1 {
    font-size: clamp(var(--step-3), 4vw, var(--step-4));
  }

  p {
    max-width: 36em;
    color: var(--ink-soft);
  }
</style>
