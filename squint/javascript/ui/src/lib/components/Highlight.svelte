<script lang="ts">
  import type { Snippet } from "svelte";

  let {
    color = "marker",
    delay,
    children,
  }: { color?: "marker" | "pink"; delay?: number; children: Snippet } = $props();
</script>

<mark class={color} class:swipe={delay !== undefined} style:--delay="{delay ?? 0}ms">
  {@render children()}
</mark>

<style>
  mark {
    --swipe-color: var(--marker);
    color: var(--on-marker);
    background: linear-gradient(100deg, var(--swipe-color), var(--swipe-color)) no-repeat left
      center / 100% 82%;
    padding-inline: 0.18em;
    margin-inline: -0.18em;
    border-radius: 0.3em 0.6em 0.4em 0.7em / 0.7em 0.35em 0.6em 0.4em;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
  }

  .pink {
    --swipe-color: var(--marker-pink);
  }

  .swipe {
    color: inherit;
    background-size: 0% 82%;
    animation:
      swipe 420ms var(--ease-out) var(--delay) forwards,
      ink 1ms linear calc(var(--delay) + 120ms) forwards;
  }

  @keyframes swipe {
    to {
      background-size: 100% 82%;
    }
  }

  @keyframes ink {
    to {
      color: var(--on-marker);
    }
  }
</style>
