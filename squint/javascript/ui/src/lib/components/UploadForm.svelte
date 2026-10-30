<script lang="ts">
  import { untrack } from "svelte";
  import { uploadDocuments } from "#lib/documents.remote.ts";
  import type { QueuedUpload } from "#lib/state/uploads.svelte.ts";

  let { upload, onsettled }: { upload: QueuedUpload; onsettled: (problems: string[]) => void } =
    $props();

  // One form instance per upload keeps each upload's issues apart
  // svelte-ignore state_referenced_locally
  const instance = uploadDocuments.for(upload.id);

  // Untracked: the submit handler runs synchronously inside requestSubmit, and any state it reads
  // would otherwise rerun this attachment and submit again
  function submitOnce(form: HTMLFormElement) {
    untrack(() => {
      const fileInput = form.querySelector<HTMLInputElement>('input[type="file"]');
      if (!upload.file || !fileInput) {
        return;
      }
      const transfer = new DataTransfer();
      transfer.items.add(upload.file);
      fileInput.files = transfer.files;
      form.requestSubmit();
    });
  }
</script>

<form
  {@attach submitOnce}
  {...instance.enhance(async ({ submit }) => {
    try {
      const succeeded = await submit();
      onsettled(succeeded ? [] : (instance.fields.allIssues() ?? []).map((issue) => issue.message));
    } catch {
      onsettled(["The upload failed. Try again."]);
    }
  })}
  enctype="multipart/form-data"
  hidden
>
  <input {...instance.fields.files.as("file multiple")} />
  <input {...instance.fields.uploadId.as("hidden", upload.id)} />
</form>
