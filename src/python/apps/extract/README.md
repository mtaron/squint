# extract

The extraction worker. It will pull schema fields out of document pages: for each value, its text
**and** its bounding box on the page. It is a scaffold for now; this README records what the
model experiments found and how to build on them.

## Model and serving

Extraction uses **Qwen3-VL-4B-Instruct** (BF16, 8.3 GiB), served by vLLM as the `qwen3-vl`
release in `infrastructure/helmfile.yaml.gotmpl`.

- Download: `task download-models`. Forward to `http://localhost:8000`: `task vllm`.
- OpenAI-compatible API, served model name `qwen3-vl`.
- Context: 12,288 tokens. In the dev GPU budget, Qwen3-VL's full-attention KV cache can't hold
  16k.
- Image cap: 4,096 visual tokens (4.2 MP). The server rejects per-request image-size overrides
  unless it runs with `--trust-request-mm-kwargs`, so the cap is a server setting.

## How to call it

One request per page:

- **Message:** the page image as a data URL, then a prompt that includes the schema's JSON Schema
  with field descriptions. Ask for each value's text exactly as printed and its
  `bbox_2d [x1, y1, x2, y2]`, relative to the image on a 0–1000 scale.
- **Output schema:** a "grounded" copy of the schema, where every string becomes
  `{text, bbox_2d}`, applied recursively to nested objects and lists. Pass it as
  `response_format: {type: json_schema}`.
- **Decoding:** `temperature=0`, `max_tokens=4096`. The Instruct model has no thinking mode.
- **Boxes:** convert to pixels with `x * width / 1000` and `y * height / 1000`. Because the boxes
  are relative, server-side resizing doesn't affect them.

`scratch/qwen_vl.py` on branch `mtaron/qwen3-vl` implements this, including the recursive
`grounded()` schema transform.

## What the experiments found

Ten models were compared on four born-digital pages:
- a title page (title and four authors with affiliations);
- two reference lists in different citation styles;
- three cells of a table with two-level column headers.

Every box was checked against the PDF text layer. The full write-up is
`scratch/vlm-extraction-findings.md` on branch `mtaron/lfm2-vl`.

Qwen3-VL-4B is the only model that both extracts values by meaning and boxes the values it
extracts:

| | Values | Boxes |
|---|---|---|
| Title page | title and 4 author names | tight on each name, without the affiliation |
| Table cells | 3/3 | 3/3 on the correct cell |
| Quoted citations | 19/19 titles | 19/19 |
| Chicago citations (small type) | 24/24 at 216 dpi (17/24 at 144 dpi) | 17/24 at 216 dpi |

Findings to keep in mind:

- **Resolution has a sweet spot, not a minimum.**
  - Letter pages worked at 144 dpi (about 2,000 visual tokens).
  - A 6×9 in page of small type needed 216 dpi (about 2,600 tokens). At 180 or 252 dpi it lost
    entries, and above the cap it got worse.
  - Choose the render scale from the text size in pixels, not a fixed dpi.
- **No model boxed small values inside a line, such as a citation's year.** Names, cells and
  titles worked; years never did, with any model or setting.
- **Field descriptions steer the values.** "Each author's name" made Qwen3.5 list affiliations
  as authors, and "…without their affiliation" fixed it. Smaller models (LFM2.5-VL, GLM-OCR)
  ignore descriptions and map the schema's keys onto the visible text instead. Whether
  Qwen3-VL-4B handles a generic `{first, last}` name without hints is untested.
- **Bigger models aren't better at boxes.** Qwen3-VL-8B (FP8) read every page correctly but
  boxed worse than the 4B. Qwen3.5 (4B and 9B) read best of all, but its boxes failed on dense
  pages, in vLLM and in the reference `transformers` implementation alike.
- **Run-to-run stability:** at temperature 0, repeated runs were identical.

## Next steps

1. **Render scale policy.**
   - Born-digital PDFs: derive the scale from the text layer's font sizes, aiming for the pixel
     text height that worked (the 216 dpi reference page).
   - Scans: estimate the text height from a low-resolution pass.
   - Calibrate on more pages than the two measured so far.
2. **Box refinement.** Treat the model's boxes as approximate locations, especially for values
   inside a line.
   - Born-digital PDFs: search the extracted text in the PDF text layer near the model's box, and
     snap to the exact character boxes. This also fixes values like years.
   - Scans: match the values against a line detector's boxes. Qwen's grounding prompt
     ("Locate every instance that belongs to the following categories…") gives exact line boxes.
3. **Evaluation set.** Turn the four test pages into a regression set and add more layouts.
   - Scoring: exact value match, and whether the PDF text inside a box contains its value. That
     check is automatic for born-digital documents.
   - Test the generic `{first, last}` name schema here before relying on description hints.
4. **Worker plumbing.** A Temporal activity that renders a page, calls the server and returns the
   grounded result.
   - Concurrency: in the dev budget the KV cache holds about one full-length request (`maxNumSeqs`
     is 8 in dev), so dev extraction is effectively sequential.
   - Measure throughput on the production GPU before sizing the worker.
