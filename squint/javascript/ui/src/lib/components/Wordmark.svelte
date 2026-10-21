<script lang="ts">
  import Mark from "./Mark.svelte";
</script>

<span class="wordmark">
  <Mark size={24} />
  <span>squint</span>
</span>

<style>
  .wordmark {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    font-family: var(--font-display);
    font-size: var(--step-3);
    font-weight: 650;
    font-variation-settings:
      "SOFT" 100,
      "WONK" 1;
    letter-spacing: -0.02em;
    line-height: 1;
  }
</style>
