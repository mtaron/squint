<script lang="ts">
  import { boxPlacement, type Box } from "#lib/search.ts";

  let { boxes }: { boxes: Box[] } = $props();
</script>

<!-- Covers its nearest positioned ancestor, which should be the size of the page image -->
<div class="boxes" aria-hidden="true">
  {#each boxes as box, index (index)}
    {@const at = boxPlacement(box)}
    <span
      data-testid="search-box"
      style:left={at.left}
      style:top={at.top}
      style:width={at.width}
      style:height={at.height}
    ></span>
  {/each}
</div>

<style>
  .boxes {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  /* Multiplied onto the page, so the print shows through like a highlighter */
  span {
    position: absolute;
    background: var(--marker);
    mix-blend-mode: multiply;
    border-radius: 0.125rem;
    outline: 0.125rem solid color-mix(in srgb, var(--marker) 60%, var(--on-marker));
    outline-offset: 0.0625rem;
  }
</style>
