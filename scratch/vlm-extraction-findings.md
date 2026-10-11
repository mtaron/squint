# Grounded schema extraction: model experiments

Goal: given a page image and a schema (e.g. `title: str`, `authors: list[str]`), return each
value's text **and** its bounding box, self-hosted on the 16 GB dev GPU (RTX 5070 Ti) with vLLM.

Every box was checked against the PDF text layer: the text inside the predicted box should be
the value. The test pages are all born-digital, so this check is exact.

## Test pages

| Test | Page | What it probes |
|---|---|---|
| Title page | ViDoRe CS, *Introduction to Python Programming*, p. 3 | 2-line title; 4 authors, each followed by an affiliation, under a "SENIOR CONTRIBUTING AUTHORS" heading |
| Chicago citations | ViDoRe pharma, *drug_resistance_book*, p. 150 | 24 dense, small-type entries; unquoted titles mid-entry |
| Quoted citations | ViDoRe HR, EU employment report 2024, p. 109 | 19 entries; year in parentheses, quoted titles |
| Table cells | ViDoRe finance, Morgan Stanley 10-K, p. 151 | 3 cells under two-level column headers (year → amount/rate) |

## Results at a glance

✅ correct · ⚠️ partly · ❌ wrong · — not tested

| Model (branch) | Title page values | Title page boxes | Citations values | Citations boxes | Table values | Table boxes |
|---|---|---|---|---|---|---|
| GutenOCR-3B (`mtaron/gutenocr`) | ⚠️ heading listed as an author; affiliations included | ✅ exact line boxes (matched to the lines it reads) | — | — | — | — |
| Qwen3.5-9B NVFP4 (`mtaron/qwen-vl`, `mtaron/qwen-4b`) | ✅ | ⚠️ right line, too wide | ✅ 24/24, 19/19 | ❌ drift down the page | ✅ 3/3 | ❌ neighbouring cells |
| Qwen3.5-4B (`mtaron/qwen-4b`) | ✅ | ❌ shifted up one line | ✅ 24/24, 19/19 | ❌ | ✅ 3/3 | ❌ |
| Claude Haiku 5.5 (`haiku_vl.py`) | ✅ (needs "capitalization included") | ⚠️ right line, too wide | — | — | — | — |
| GLM-OCR 0.9B (`mtaron/glm-ocr`) | ⚠️ exact only with a tuned template | — (KIE has no boxes) | ⚠️ entries and years right; "title" holds the whole citation | — | — | — |
| **Qwen3-VL-4B** (`mtaron/qwen3-vl`) | ✅ | ✅ tight on the names | ✅ quoted 19/19; Chicago 17/24 at 144 dpi, **24/24 at 216 dpi** | ✅ quoted 19/19; Chicago 17/24 at 216 dpi | ✅ 3/3 | ✅ 3/3 |
| Qwen3-VL-8B FP8 (`mtaron/qwen3-vl`) | ✅ | ⚠️ too wide | ✅ 24/24 at every dpi, 19/19 | ❌ quoted 3/19; Chicago 16/24 at best | ✅ 3/3 | ❌ 1/3 |
| LFM2.5-VL-450M (`mtaron/lfm2-vl`) | ⚠️ title only; affiliations listed as authors | ❌ | ❌ collapsed, or runs to the token limit | ❌ | ❌ wrong cells | ❌ |
| LFM2.5-VL-1.6B (`mtaron/lfm2-vl`) | ⚠️ title right; authors keep affiliations | ⚠️ title exact; no author boxes | ⚠️ Chicago: 24/24 entries and years, but titles hold the whole citation; quoted: collapsed | ❌ | ❌ echoes the field descriptions | ❌ |

No model ever boxed a citation's **year** correctly: the boxes land at the start of the entry.

## Recommendation

**Qwen3-VL-4B-Instruct** (8.3 GiB BF16) is the only model that both extracts by meaning and
boxes the values it extracts.

- **Render scale:** pick it per page from the text size in pixels, not a fixed dpi. Letter pages
  worked at 144 dpi. The 6×9 in book page needed 216 dpi, and 180 or 252 dpi each lost entries.
- **Small values inside a line:** values such as years still need boxes from text matching. For
  born-digital PDFs, search the extracted string in the PDF text layer, which gives exact
  boxes. For scans, match the values against a line reader's boxes (Qwen's grounding prompt,
  GutenOCR or GLM-OCR all give exact line boxes).
- **Bigger models and their boxes:** the boxes got *worse* with size (Qwen3-VL-8B FP8 against
  the 4B). Use a larger model for reading only if the 4B misses values.

## What each experiment taught

### GutenOCR-3B: grounded OCR, not extraction
- Full-page line reading gives exact text and exact line boxes.
- "Highlight the title" behaves as a **string search**: it boxed the word "AUTHORS". The
  model has no notion of schema fields.
- What remains of Qwen2.5-VL's instruction following works only under Qwen's default system
  prompt; GutenOCR's own prompt forces a line dump. It still copies whole lines (heading and
  affiliations included), and field descriptions made no difference.
- Matching the extracted values to the line-level read gave exact boxes, including one box
  over the 2-line title.
- Gotcha: the HF repo's sharded weights lack `lm_head.weight`. Use `model.safetensors` only.

### Qwen3.5 (9B NVFP4 and 4B BF16): best reading, broken grounding
- Every value was correct on every page, including clean citation titles and two-level table
  headers.
- The field description decides the answer: "Each author's name" listed affiliations as
  authors; "…without their affiliation" fixed it. Thinking mode didn't help and was 2–17×
  slower.
- Boxes fail on dense pages. The reference `transformers` implementation reproduced the same
  offsets as vLLM (4B: y −25/1000 on the title page; vertical positions unrelated to the real
  lines on the reference list), so it is the model, not serving.
- Qwen's grounding prompt (the cookbook's) gives exact **line** boxes but no semantic
  filtering. The category wording matters: a bare "title" returned nothing, "author" returned
  the whole block, and "person name" returned names with boxes cut short.
- Serving: needs `maxNumSeqs: 8`. The default of 256 runs out of GPU memory on the hybrid
  GatedDeltaNet state and CUDA graphs.

### Claude Haiku 5.5: cheap cloud baseline
- The right four names with thinking off and effort `low`: about 1,208 input and 163 output
  tokens, about $0.0002 per page (72 dpi image, about 650 image tokens).
- Haiku 5.5 rejects `temperature`, so the prompt has to pin the format; "capitalization
  included" removed the run-to-run variation.
- Boxes: right line, too wide, the same failure as Qwen3.5.

### GLM-OCR 0.9B: excellent reader, weak on field meaning
- The KIE prompt is fixed (a Chinese instruction plus a JSON template), and the model sees only
  the template's **keys**. Descriptions never reach it.
- The template's shape acts as the instruction:
  - a list of N strings returns N items;
  - `[{"name": ""}]` returns whole lines;
  - `[{"name": "", "affiliation": ""}]` returns the exact names.
- Citations: every entry and year was correct, but `title` held the whole citation. Adding
  `authors` and `publication` keys fixed one citation style and broke the other (dropped an
  entry, then looped to the token limit). Templates don't generalize across layouts.
- Gotcha: the SDK's `repetition_penalty` of 1.1 drops a comma after about 20 list items, so the
  JSON is invalid. Enforce the schema and drop the penalty.
- Small and fast: 3.7 GiB, about 5 s for a dense reference page.

### Qwen3-VL (4B BF16, 8B FP8): the grounding cookbooks' actual target
- The 4B fixed grounding: title-page lines within 3/1000, names boxed without affiliations, and
  all three table cells on the right cell.
- Resolution has a sweet spot. On the small-type reference page, 216 dpi gave 24/24 titles in
  order; 144 dpi gave 17/24, and 288 dpi gave 15/24.
- The 8B reads more robustly (24/24 at every dpi) but grounds worse. This could be the FP8
  quantization; BF16 doesn't fit the GPU to check.
- Serving: Qwen3-VL's full-attention KV cache can't hold a 16k context in the dev budget, so the
  release uses 12,288 tokens. The 8B needs `gpuMemoryUtilization: 0.85`, which leaves no room for
  the embed worker.

### LFM2.5-VL (450M and 1.6B): built for simple fields
- Run the way Liquid's invoice-parser cookbook does it: a plain-language list of field
  descriptions placed before the image, temperature 0, the schema enforced, then each value
  located with the model card's detection prompt.
- The cookbook's fields (amount, currency, utility) are large and unambiguous, and that is the
  limit of what works:
  - The 1.6B gets the title, and boxes it exactly.
  - It finds all 24 Chicago entries and years, but puts the whole citation in `title`.
  - On harder fields it returns the field descriptions themselves as values.
- The 450M splits names from affiliations, then lists each affiliation as an author; its
  values and boxes are wrong elsewhere. Its card warns it is not suited to fine-grained OCR.
- Only the 450M's card claims boxes. The 1.6B's detection runs away (coordinates outside [0, 1],
  detections until the token limit) unless the schema caps both.
- Serving: the 0.9 and 3.2 GB models fit in 0.3 of the GPU. Small models need vLLM's
  `--structured-outputs-config '{"backend": "xgrammar", "disable_any_whitespace": true}'`,
  or schema-enforced output can run to the token limit in whitespace.

## Serving notes (vLLM v0.31.0 on the 16 GB dev GPU)

| Model | Weights | Dev GPU share | Notes |
|---|---|---|---|
| GutenOCR-3B | 7.5 GiB | 0.72 | `--generation-config vllm` to drop the checkpoint's `repetition_penalty` |
| Qwen3.5-9B NVFP4 | 8.4 GiB | 0.72 | `maxNumSeqs: 8`; FlashInfer NVFP4 kernels on Blackwell |
| Qwen3.5-4B | 8.7 GiB | 0.72 | `maxNumSeqs: 8` |
| GLM-OCR | 2.5 GiB | 0.4 | MTP speculative decoding (1 token) |
| Qwen3-VL-4B | 8.3 GiB | 0.72 | `maxModelLen: 12288` |
| Qwen3-VL-8B FP8 | 9.9 GiB | 0.85 | no room for the embed worker |
| LFM2.5-VL-450M | 0.9 GiB | 0.3 | native tiling (10 tiles of 512 px plus a thumbnail) |
| LFM2.5-VL-1.6B | 3.2 GiB | 0.3 | `--state-values-set lfm-vl.model=LFM2.5-VL-1.6B` |

- The Qwen release takes `--state-values-set qwen-vl.model=…,qwen-vl.maxImageTokens=…,qwen-vl.gpuMemoryUtilization=…`
  (branches `mtaron/qwen-4b` and `mtaron/qwen3-vl`).
- Per-request `mm_processor_kwargs` are rejected unless the server runs with
  `--trust-request-mm-kwargs`, so the image cap is a server setting.
