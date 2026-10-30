<script lang="ts">
  import { resolve } from "$app/paths";
  import HeroDemo from "#lib/components/HeroDemo.svelte";

  const steps = [
    {
      title: "Add your documents",
      body: "Upload a single PDF or a whole folder. squint embeds each page as an image, with no OCR or PDF parsing.",
    },
    {
      title: "Define a schema",
      body: "Name the fields you want, like vendor, invoice number, and total due. One schema covers every document, so you don't maintain a template for each layout.",
    },
    {
      title: "Get a table back",
      body: "Each document becomes a row, and each value points to the spot on the page it came from, so you can check the results.",
    },
  ];
</script>

<section class="hero">
  <div class="pitch">
    <h1>Turn a thousand PDFs into one table.</h1>
    <p class="lede">
      Tell squint which fields you need. It finds them across your documents, scanned or digital,
      and shows you where on the page each value came from.
    </p>
    <div class="actions">
      <a class="button" href={resolve("/login")}>Get started</a>
      <a class="button quiet" href="#self-host">Run it yourself</a>
    </div>
  </div>
  <HeroDemo />
</section>

<section class="steps" aria-labelledby="steps-heading">
  <h2 id="steps-heading">How it works</h2>
  <ol>
    {#each steps as step (step.title)}
      <li>
        <h3>{step.title}</h3>
        <p>{step.body}</p>
      </li>
    {/each}
  </ol>
</section>

<section class="vision" aria-labelledby="vision-heading">
  <div>
    <h2 id="vision-heading">No parsing, just pixels</h2>
    <p>
      Most document pipelines start with OCR, page segmentation, and reading order reconstruction.
      squint skips those steps. It embeds page images directly to find the right pages, then a
      vision-language model reads them.
    </p>
  </div>
  <ul>
    <li>
      <span class="i-ph-layout-duotone" aria-hidden="true"></span>
      <div>
        <h3>Layout stays intact</h3>
        <p>The model sees the whole page, so tables and forms keep their structure.</p>
      </div>
    </li>
    <li>
      <span class="i-ph-scan-duotone" aria-hidden="true"></span>
      <div>
        <h3>Scans work too</h3>
        <p>A scanned PDF goes through the same pipeline as a born-digital one.</p>
      </div>
    </li>
    <li>
      <span class="i-ph-gauge-duotone" aria-hidden="true"></span>
      <div>
        <h3>Small models, only when needed</h3>
        <p>
          squint favors small models and saves per-page work until a schema calls for it, which
          keeps cost per page low.
        </p>
      </div>
    </li>
  </ul>
</section>

<section id="self-host" class="self-host" aria-labelledby="self-host-heading">
  <span class="i-ph-hard-drives-duotone" aria-hidden="true"></span>
  <h2 id="self-host-heading">Your documents stay on your GPUs</h2>
  <p>
    squint runs on your own Kubernetes cluster, next to your data. The models run there too, so your
    pages never leave your infrastructure.
  </p>
</section>

<style>
  section + section {
    margin-block-start: var(--space-9);
  }

  .hero {
    display: grid;
    gap: var(--space-8);
    align-items: center;
    padding-block-start: var(--space-7);

    @media (min-width: 60rem) {
      grid-template-columns: 1.1fr 1fr;
      gap: var(--space-7);
      padding-block-start: var(--space-8);
    }
  }

  .pitch {
    display: grid;
    gap: var(--space-5);
  }

  .lede {
    max-width: 34em;
    color: var(--ink-soft);
    font-size: var(--step-2);
    line-height: 1.45;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
    margin-block-start: var(--space-2);
  }

  .steps ol {
    display: grid;
    gap: var(--space-6);
    margin-block-start: var(--space-6);
    padding: 0;
    list-style: none;
    counter-reset: step;

    @media (min-width: 48rem) {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .steps li {
    display: grid;
    align-content: start;
    gap: var(--space-2);
    padding-block-start: var(--space-4);
    border-top: 1px solid var(--ink);
    counter-increment: step;

    &::before {
      content: counter(step);
      justify-self: start;
      padding-inline: 0.15em;
      padding-block-end: 0.12em;
      margin-block-end: var(--space-2);
      font-family: var(--font-display);
      font-size: var(--step-4);
      font-variation-settings:
        "SOFT" 100,
        "WONK" 1;
      font-weight: 600;
      line-height: 1;
      background: linear-gradient(var(--marker-pink), var(--marker-pink)) no-repeat 0 100% / 100%
        0.22em;
    }

    p {
      color: var(--ink-soft);
    }
  }

  .vision {
    display: grid;
    gap: var(--space-6);

    @media (min-width: 60rem) {
      grid-template-columns: 1fr 1fr;
      gap: var(--space-8);
    }

    > div {
      display: grid;
      align-content: start;
      gap: var(--space-4);
    }

    ul {
      display: grid;
      gap: var(--space-5);
      padding: 0;
      list-style: none;
    }

    li {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: var(--space-4);
      align-items: start;
    }

    li p {
      color: var(--ink-soft);
    }

    [class^="i-ph"] {
      font-size: var(--step-4);
    }
  }

  .self-host {
    display: grid;
    gap: var(--space-4);
    padding-block-start: var(--space-7);
    border-top: 1px solid var(--rule);

    [class^="i-ph"] {
      font-size: var(--step-5);
    }
  }
</style>
