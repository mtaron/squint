import { resolve } from "$app/paths";
import { getDocuments } from "#lib/documents.remote.ts";

/** XMLHttpRequest rather than fetch, which can't report how much of a request body has been sent. */
function post(file: File, onProgress: (loaded: number) => void): Promise<XMLHttpRequest> {
  return new Promise((done) => {
    const request = new XMLHttpRequest();
    request.open("POST", resolve("/documents"));
    request.responseType = "json";
    request.setRequestHeader("accept", "application/json");
    request.setRequestHeader("content-type", "application/pdf");
    request.setRequestHeader("file-name", encodeURIComponent(file.name));
    request.upload.onprogress = ({ loaded }) => onProgress(loaded);
    request.onloadend = () => done(request);
    request.send(file);
  });
}

/** Sends a PDF as the raw request body, so the server can stream it on to S3 as it arrives. */
export async function sendUpload(
  file: File,
  onProgress: (loaded: number) => void,
): Promise<string[]> {
  const { status, response } = await post(file, onProgress);
  if (status === 422) {
    return [response.problem];
  }
  if (status !== 201) {
    throw new Error(`Upload failed with status ${status}`);
  }
  // Before the row leaves the queue, so the document can take its place
  await getDocuments()
    .refresh()
    .catch((error) => console.error("Failed to refresh the document list", error));
  return [];
}
