<script lang="ts">
  import { resolve } from "$app/paths";
  import SystemDiagram from "#lib/components/SystemDiagram.svelte";

  const repository = "https://github.com/mtaron/squint";

  const principles = [
    {
      name: "Vision-first",
      body: "A scanned PDF and a born-digital one take the same path. No PDF parsing, just pixels.",
    },
    {
      name: "Efficient",
      body: "How low can cost per page go with small models while the results stay acceptable?",
    },
    {
      name: "Lazy",
      body: "Most per-page work is never looked at. Put it off until someone actually needs it.",
    },
    {
      name: "Self-hostable",
      body: "Everything runs on one Kubernetes cluster, which keeps GPU bills down during development.",
    },
  ];

  const parts = [
    {
      name: "NeoMME",
      role: "page embeddings",
      href: "https://huggingface.co/blog/Hcompany/neomme",
    },
    {
      name: "Qwen3.5 4B",
      role: "vision-language model",
      href: "https://huggingface.co/Qwen/Qwen3.5-4B",
    },
    { name: "vLLM", role: "model serving", href: "https://docs.vllm.ai/" },
    { name: "Temporal", role: "durable workers", href: "https://docs.temporal.io/" },
    { name: "Milvus", role: "vector store", href: "https://milvus.io/docs" },
    { name: "Dragonfly", role: "key-value store", href: "https://www.dragonflydb.io/docs" },
    { name: "SvelteKit", role: "this UI", href: "https://svelte.dev/docs/kit/introduction" },
    { name: "agentgateway", role: "networking", href: "https://agentgateway.dev/" },
  ];
</script>

<section class="hero">
  <div class="pitch">
    <h1>A self-hosted playground for vision-first document understanding</h1>
    <p class="lede">
      squint is a side project for exploring a new wave of AI models for document understanding.
      Older approaches started with the text and tried to recover the meaning trapped in layout and
      tables. Modern models like <a href="https://huggingface.co/blog/manu/colpali">ColPali</a> start
      with the page images instead. squint is a self-hostable app that lets me explore some ideas without
      breaking the bank.
    </p>
    <div class="actions">
      <a class="button" href={repository}>Read the code</a>
      <a class="button quiet" href={resolve("/login")}>Try the app</a>
    </div>
  </div>
  <SystemDiagram />
</section>

<section class="details">
  <div>
    <h2 id="principles-heading">Principles</h2>
    <dl aria-labelledby="principles-heading">
      {#each principles as principle (principle.name)}
        <div>
          <dt>{principle.name}</dt>
          <dd>{principle.body}</dd>
        </div>
      {/each}
    </dl>
  </div>

  <div>
    <h2 id="parts-heading">Parts</h2>
    <ul class="parts" aria-labelledby="parts-heading">
      {#each parts as part (part.name)}
        <li><a href={part.href}>{part.name}</a> <span>{part.role}</span></li>
      {/each}
    </ul>
    <p class="dev-loop">
      The other half of the experiment is the dev loop: a local kind cluster with GPU access, Tilt
      for live reload, and remote debugging into every container. Nothing runs outside the cluster.
    </p>
  </div>
</section>

<style>
  section + section {
    margin-block-start: var(--space-9);
  }

  .hero {
    display: grid;
    gap: var(--space-7);
    align-items: center;
    padding-block-start: var(--space-7);

    @media (min-width: 60rem) {
      grid-template-columns: 1.1fr 1fr;
      padding-block-start: var(--space-8);
    }
  }

  .pitch {
    display: grid;
    gap: var(--space-5);

    h1 {
      font-size: clamp(var(--step-4), 4.5vw, var(--step-5));
      line-height: 1.05;
    }
  }

  .lede {
    max-width: 32em;
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

  .details {
    display: grid;
    gap: var(--space-8);
    padding-block-start: var(--space-7);
    border-top: 1px solid var(--rule);

    @media (min-width: 60rem) {
      grid-template-columns: 1.2fr 1fr;
      gap: var(--space-8);
    }

    > div {
      display: grid;
      align-content: start;
      gap: var(--space-5);
    }
  }

  dl {
    display: grid;
    gap: var(--space-5);

    @media (min-width: 40rem) {
      grid-template-columns: 1fr 1fr;
    }
  }

  dt {
    font-weight: 650;
  }

  dd {
    margin: 0;
    color: var(--ink-soft);
  }

  .parts {
    display: grid;
    gap: var(--space-2);
    padding: 0;
    list-style: none;

    li {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 0 var(--space-4);
      padding-block-end: var(--space-2);
      border-bottom: 1px solid var(--rule);
    }

    span {
      color: var(--ink-soft);
    }
  }

  .dev-loop {
    color: var(--ink-soft);
  }
</style>
