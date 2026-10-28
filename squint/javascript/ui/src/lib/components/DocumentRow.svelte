<script lang="ts">
  import { enhance } from "$app/forms";
  import Button from "#lib/components/Button.svelte";
  import type { DocumentSummary } from "#lib/uploads/documents.ts";
  import { ingestErrorCopy } from "#lib/uploads/errors.ts";
  import { plural } from "#lib/uploads/format.ts";

  type Props = { document: DocumentSummary; showUploadDate: boolean };

  let { document, showUploadDate }: Props = $props();

  let replacing = $state(false);

  const problem = $derived(document.errorCode ? ingestErrorCopy[document.errorCode] : undefined);
  const retryable = $derived(document.errorCode === "internal");

  // Fixed to UTC so the server and browser render the same text
  const uploadDate = new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  });

  const statusLabels = { processing: "Processing", ready: "Ready", failed: "Failed" } as const;
  const statusIcons = {
    processing: "i-ph-circle-notch",
    ready: "i-ph-check-circle",
    failed: "i-ph-warning-circle-fill",
  } as const;
</script>

{#snippet row()}
  <span class="kind i-ph-file-pdf-duotone" aria-hidden="true"></span>
  <span class="name">
    {document.name}
    {#if showUploadDate}
      <time datetime={document.uploadedAt.toISOString()}>
        uploaded {uploadDate.format(document.uploadedAt)} UTC
      </time>
    {/if}
  </span>
  <span class="pages">
    {document.pageCount === null ? "" : plural(document.pageCount, "page")}
  </span>
  <span class={["status", document.status]}>
    <span class={statusIcons[replacing ? "processing" : document.status]} aria-hidden="true"></span>
    {replacing ? "Replacing" : statusLabels[document.status]}
  </span>
{/snippet}

<li>
  {#if document.status === "failed"}
    <details>
      <summary class="row">{@render row()}</summary>
      <div class="problem">
        {#if problem}
          <p class="title">{problem.title}</p>
          <p>{problem.remedy}</p>
        {/if}
        {#if document.errorDetail}
          <details class="detail">
            <summary>Details</summary>
            <pre>{document.errorDetail}</pre>
          </details>
        {/if}
        <div class="actions">
          {#if retryable}
            <form method="POST" action="?/retry" use:enhance>
              <input type="hidden" name="documentId" value={document.id} />
              <Button>Try again</Button>
            </form>
          {/if}
          <form
            method="POST"
            action="?/replace"
            enctype="multipart/form-data"
            use:enhance={() => {
              replacing = true;
              return async ({ update }) => {
                await update();
                replacing = false;
              };
            }}
          >
            <!-- Before the file, so the server knows which document it replaces as the file arrives -->
            <input type="hidden" name="documentId" value={document.id} />
            <Button as="label" variant={retryable ? "quiet" : "primary"}>
              Replace with another PDF
              <input
                class="visually-hidden"
                type="file"
                name="file"
                accept=".pdf,application/pdf"
                required
                onchange={(event) => event.currentTarget.form?.requestSubmit()}
              />
            </Button>
            <noscript><Button variant="quiet">Upload replacement</Button></noscript>
          </form>
          <form method="POST" action="?/delete" use:enhance>
            <input type="hidden" name="documentId" value={document.id} />
            <Button variant="quiet">Delete</Button>
          </form>
        </div>
      </div>
    </details>
  {:else}
    <div class="row">{@render row()}</div>
  {/if}
</li>

<style>
  li {
    border-bottom: 1px solid var(--rule);
  }

  .row {
    display: grid;
    grid-template-columns: auto 1fr auto auto;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-3) var(--space-2);
    font-size: var(--step-0);
  }

  summary.row {
    cursor: pointer;
    list-style: none;

    &::-webkit-details-marker {
      display: none;
    }

    &:hover {
      background: var(--surface);
    }
  }

  .kind {
    font-size: var(--step-3);
    color: var(--ink-soft);
  }

  .name {
    display: grid;
    min-width: 0;
    overflow-wrap: anywhere;
    font-weight: 600;
  }

  time,
  .pages {
    color: var(--ink-soft);
    font-weight: 400;
    font-size: var(--step--1);
  }

  .status {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    min-width: 7.5rem;
    color: var(--ink-soft);

    &.failed {
      color: var(--danger);
      font-weight: 600;
    }
  }

  .i-ph-circle-notch {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      rotate: 1turn;
    }
  }

  .problem {
    display: grid;
    gap: var(--space-3);
    margin: 0 var(--space-2) var(--space-4) calc(var(--step-3) + var(--space-6));
    padding: var(--space-4);
    background: var(--surface);
    border-inline-start: 3px solid var(--danger);
    border-radius: var(--radius-small);
    font-size: var(--step-0);

    .title {
      font-weight: 600;
    }

    @media (max-width: 40rem) {
      margin-inline-start: var(--space-2);
    }
  }

  .detail {
    color: var(--ink-soft);

    summary {
      cursor: pointer;
    }

    pre {
      margin-block-start: var(--space-2);
      font-size: var(--step--1);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
  }

  @media (max-width: 40rem) {
    .row {
      grid-template-columns: auto 1fr auto;
    }

    .pages {
      display: none;
    }

    .status {
      min-width: 0;
    }
  }
</style>
