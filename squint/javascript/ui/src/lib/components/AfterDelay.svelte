<script lang="ts">
  import type { Snippet } from "svelte";

  let { ms, children }: { ms: number; children: Snippet } = $props();

  let elapsed = $state(false);

  $effect(() => {
    const timer = setTimeout(() => {
      elapsed = true;
    }, ms);
    return () => clearTimeout(timer);
  });
</script>

{#if elapsed}
  {@render children()}
{/if}
