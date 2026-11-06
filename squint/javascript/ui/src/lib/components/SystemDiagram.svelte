<script lang="ts">
  import Highlight from "./Highlight.svelte";

  const arrowStagger = 160;
  const arrowDelay = (order: number) => `${300 + order * arrowStagger}ms`;
  const answerDelay = 300 + 9 * arrowStagger + 200;

  const arrows = [
    { row: "3", column: "1", order: 0 },
    { row: "5", column: "1", order: 1 },
    { row: "7", column: "1", order: 2 },
    { row: "9", column: "1", order: 3 },
    { row: "3 / 8", column: "3", order: 4 },
    { row: "9", column: "3", order: 5 },
    { row: "11", column: "3", order: 7 },
    { row: "13", column: "3", order: 8 },
  ];
</script>

<figure class="system" style:--answer-delay="{answerDelay}ms">
  <div class="grid">
    <p class="lane" style:grid-area="1 / 1">Ingest</p>
    <div class="node" style:grid-area="2 / 1">
      <span class="i-ph-upload-simple-duotone" aria-hidden="true"></span>
      <p><strong>Upload</strong> PDFs from the browser</p>
    </div>
    <div class="node" style:grid-area="4 / 1">
      <span class="i-ph-hard-drives-duotone" aria-hidden="true"></span>
      <p><strong>S3</strong> stores the PDF and page images</p>
    </div>
    <div class="node" style:grid-area="6 / 1">
      <span class="i-ph-gear-six-duotone" aria-hidden="true"></span>
      <p><strong>Ingest worker</strong> rasterizes every page to an image</p>
    </div>

    <div class="node model" style:grid-area="8 / 1 / 9 / 4">
      <span class="i-ph-grid-nine-duotone" aria-hidden="true"></span>
      <p><strong>NeoMME</strong> embeds page images and questions as patch vectors</p>
    </div>

    <div class="node" style:grid-area="10 / 1">
      <span class="i-ph-database-duotone" aria-hidden="true"></span>
      <p><strong>Milvus</strong> indexes the page vectors</p>
    </div>

    <p class="lane" style:grid-area="1 / 3">Search</p>
    <div class="node question" style:grid-area="2 / 3">
      <span class="i-ph-magnifying-glass-duotone" aria-hidden="true"></span>
      <p>When did the Harrow &amp; Vale statement arrive?</p>
    </div>
    <span
      class="arrow across"
      style:grid-area="10 / 2"
      style:--delay={arrowDelay(6)}
      aria-hidden="true"
    ></span>
    <div class="node" style:grid-area="10 / 3">
      <span class="i-ph-gear-six-duotone" aria-hidden="true"></span>
      <p><strong>Search worker</strong> ranks pages in Milvus</p>
    </div>
    <div class="node model" style:grid-area="12 / 3">
      <span class="i-ph-eye-duotone" aria-hidden="true"></span>
      <p><strong>Qwen3.5 4B</strong> reads the top pages and finds the answer</p>
    </div>
    <div class="node answer" style:grid-area="14 / 3">
      <svg viewBox="0 0 34 44" aria-hidden="true">
        <rect class="sheet" x="0.5" y="0.5" width="33" height="43" rx="1.5" />
        <path class="lines" d="M5 6h14M5 9h9M5 14h24M5 17h24M5 20h24M5 23h18M5 27h24" />
        <g transform="rotate(-9 24 34)">
          <rect class="stamp" x="17" y="30.5" width="13" height="7" rx="1" />
        </g>
        <rect class="found" x="15" y="28" width="17.5" height="12" rx="1.5" />
      </svg>
      <p>
        <Highlight delay={answerDelay}>Received 3 Nov 2026</Highlight>, stamped on page 1
      </p>
    </div>

    {#each arrows as arrow (arrow.order)}
      <span
        class="arrow"
        style:grid-row={arrow.row}
        style:grid-column={arrow.column}
        style:--delay={arrowDelay(arrow.order)}
        aria-hidden="true"
      ></span>
    {/each}

    <p class="note" style:grid-area="12 / 1 / 15 / 2">
      Both flows are Temporal workflows on one Kubernetes cluster. Qwen reads the page images
      straight from S3, so no text is ever extracted.
    </p>
  </div>
</figure>

<style>
  .system {
    margin: 0;
  }

  .grid {
    --arrow-gap: 1.75rem;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 2.5rem minmax(0, 1fr);
    grid-template-rows:
      auto auto var(--arrow-gap) auto var(--arrow-gap) auto var(--arrow-gap) auto
      var(--arrow-gap) auto var(--arrow-gap) auto var(--arrow-gap) auto;
    font-size: var(--step--1);
    line-height: 1.35;
  }

  .lane {
    padding-block-end: var(--space-2);
    font-family: var(--font-display);
    font-size: var(--step-1);
    font-variation-settings:
      "SOFT" 100,
      "WONK" 1;
    font-weight: 600;
  }

  .node {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    gap: var(--space-2);
    align-items: start;
    padding: var(--space-3);
    background: var(--surface);
    border: 1px solid var(--rule);
    border-radius: var(--radius-small);

    p {
      color: var(--ink-soft);
    }

    strong {
      display: block;
      color: var(--ink);
      font-weight: 650;
    }

    [class^="i-ph"] {
      font-size: var(--step-2);
    }
  }

  .model {
    border-color: var(--ink);
  }

  .question {
    align-items: center;
    border-color: var(--ink);
    border-radius: 1.25rem;

    p {
      color: var(--ink);
      font-style: italic;
    }
  }

  .answer {
    align-items: center;

    svg {
      width: 2.25rem;
      height: auto;
    }

    p {
      color: var(--ink-soft);
    }
  }

  .sheet {
    fill: var(--paper);
    stroke: var(--rule);
  }

  .lines {
    stroke: var(--rule);
    stroke-width: 1.4;
    stroke-linecap: round;
  }

  .stamp {
    fill: none;
    stroke: #c2414c;
    stroke-width: 1.2;
  }

  .found {
    fill: color-mix(in oklab, var(--marker) 40%, transparent);
    stroke: var(--marker);
    stroke-width: 1.4;
    opacity: 0;
    animation: appear 300ms var(--ease-out) var(--answer-delay) forwards;
  }

  .arrow {
    position: relative;
    justify-self: center;
    width: 1.5px;
    background: var(--ink-soft);
    transform-origin: top;
    animation: grow 260ms var(--ease-out) var(--delay) both;

    &::after {
      content: "";
      position: absolute;
      inset-block-end: -1px;
      inset-inline-start: 50%;
      translate: -50% 0;
      border: 4px solid transparent;
      border-block-end: 0;
      border-block-start: 6px solid var(--ink-soft);
    }
  }

  .across {
    justify-self: stretch;
    align-self: center;
    width: auto;
    height: 1.5px;
    margin-inline: var(--space-1);
    transform-origin: left;
    animation-name: grow-across;

    &::after {
      inset-block-end: auto;
      inset-block-start: 50%;
      inset-inline-start: auto;
      inset-inline-end: -1px;
      translate: 0 -50%;
      border: 4px solid transparent;
      border-inline-end: 0;
      border-inline-start: 6px solid var(--ink-soft);
    }
  }

  .note {
    align-self: end;
    padding-inline-end: var(--space-3);
    color: var(--ink-soft);
  }

  @keyframes grow {
    from {
      transform: scaleY(0);
    }
  }

  @keyframes grow-across {
    from {
      transform: scaleX(0);
    }
  }

  @keyframes appear {
    to {
      opacity: 1;
    }
  }
</style>
