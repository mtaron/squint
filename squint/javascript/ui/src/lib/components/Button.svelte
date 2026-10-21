<script lang="ts">
  import type { Snippet } from "svelte";
  import type { HTMLAnchorAttributes, HTMLButtonAttributes } from "svelte/elements";

  type Props = { variant?: "primary" | "quiet"; children: Snippet } & (
    | ({ href: string } & HTMLAnchorAttributes)
    | ({ href?: undefined } & HTMLButtonAttributes)
  );

  let { variant = "primary", children, ...rest }: Props = $props();
</script>

{#if rest.href !== undefined}
  <a class="button {variant}" {...rest as HTMLAnchorAttributes}>{@render children()}</a>
{:else}
  <button class="button {variant}" {...rest as HTMLButtonAttributes}>{@render children()}</button>
{/if}

<style>
  .button {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-5);
    border: 1px solid transparent;
    border-radius: var(--radius-small);
    font-size: var(--step-0);
    font-weight: 600;
    line-height: 1.2;
    text-decoration: none;
    cursor: pointer;
    transition:
      box-shadow 160ms var(--ease-out),
      background-color 160ms var(--ease-out);
  }

  .primary {
    background: var(--ink);
    color: var(--paper);

    &:hover {
      box-shadow: inset 0 -0.3em 0 var(--marker);
    }
  }

  .quiet {
    background: transparent;
    color: var(--ink);
    border-color: var(--rule);

    &:hover {
      background: var(--surface);
    }
  }
</style>
