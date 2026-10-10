Title: GutenOCR: A Grounded Vision–Language Front-End for Documents

URL Source: https://arxiv.org/html/2601.14490

Published Time: Fri, 23 Jan 2026 01:57:54 GMT

Markdown Content:
###### Abstract

GutenOCR is a family of grounded OCR front-ends obtained by fine-tuning Qwen2.5-VL-3B and Qwen2.5-VL-7B. The resulting single-checkpoint vision–language models expose reading, detection, and grounding through a unified, prompt-based interface. Trained on business documents, scientific articles, and synthetic grounding data, the models support full-page and localized reading with line- and paragraph-level bounding boxes and conditional “where is x?” queries. We introduce a grounded OCR evaluation protocol and show that GutenOCR-7B more than doubles the composite grounded OCR score of its Qwen2.5-VL-7B backbone on 10.5K held-out business and scientific pages (0.40→\rightarrow 0.82). On Fox and OmniDocBench v1.5, our approach substantially improves region- and line-level OCR as well as text-detection recall, but reveals trade-offs in page-level linearization, color-guided OCR, and formula-heavy layouts.

![Image 1: [Uncaptioned image]](https://arxiv.org/html/2601.14490v2/x1.png)

Figure 1:  Capability profile of GutenOCR-3B/7B, their Qwen2.5-VL backbones, and Qwen2.5-based OCR baselines on nine grounded OCR tasks spanning our in-domain suite and Fox. Each spoke shows a raw score in [0,1][0,1] (higher is better): in-domain page-, line-, and local-reading tasks are scored as 1−CER 1-\mathrm{CER}, full and conditional detection as F1, and Fox page-, region-, line-, and color-guided OCR as 1−CER 1-\mathrm{CER}. GutenOCR substantially improves detection, fine-grained reading, and Fox region/line OCR, while trading off some page-level and color-guided performance relative to OCR-specialized baselines. 

###### Contents

1.   [1 Introduction](https://arxiv.org/html/2601.14490v2#S1 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
2.   [2 GutenOCR Overview](https://arxiv.org/html/2601.14490v2#S2 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [2.1 Model Overview](https://arxiv.org/html/2601.14490v2#S2.SS1 "In 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [2.2 Task Families and Interfaces](https://arxiv.org/html/2601.14490v2#S2.SS2 "In 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

3.   [3 Data & Training](https://arxiv.org/html/2601.14490v2#S3 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [3.1 Data curation](https://arxiv.org/html/2601.14490v2#S3.SS1 "In 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [3.2 Training recipe](https://arxiv.org/html/2601.14490v2#S3.SS2 "In 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

4.   [4 Evaluation Setup](https://arxiv.org/html/2601.14490v2#S4 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [4.1 Metrics](https://arxiv.org/html/2601.14490v2#S4.SS1 "In 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [4.2 Benchmarks](https://arxiv.org/html/2601.14490v2#S4.SS2 "In 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

5.   [5 Results](https://arxiv.org/html/2601.14490v2#S5 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [5.1 Models](https://arxiv.org/html/2601.14490v2#S5.SS1 "In 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [5.2 In-Domain](https://arxiv.org/html/2601.14490v2#S5.SS2 "In 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    3.   [5.3 Fox](https://arxiv.org/html/2601.14490v2#S5.SS3 "In 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    4.   [5.4 OmniDocBench v1.5](https://arxiv.org/html/2601.14490v2#S5.SS4 "In 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        1.   [5.4.1 Text Recognition](https://arxiv.org/html/2601.14490v2#S5.SS4.SSS1 "In 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        2.   [5.4.2 Text Detection](https://arxiv.org/html/2601.14490v2#S5.SS4.SSS2 "In 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        3.   [5.4.3 Formula Recognition](https://arxiv.org/html/2601.14490v2#S5.SS4.SSS3 "In 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

    5.   [5.5 Training Stage Ablation](https://arxiv.org/html/2601.14490v2#S5.SS5 "In 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    6.   [5.6 Qualitative Examples](https://arxiv.org/html/2601.14490v2#S5.SS6 "In 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

6.   [6 Discussion](https://arxiv.org/html/2601.14490v2#S6 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
7.   [7 Related Work](https://arxiv.org/html/2601.14490v2#S7 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [7.1 Classical and Modern OCR Pipelines](https://arxiv.org/html/2601.14490v2#S7.SS1 "In 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [7.2 Document Conversion Toolchains and Markup Formats](https://arxiv.org/html/2601.14490v2#S7.SS2 "In 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    3.   [7.3 Vision–Language Models for Documents](https://arxiv.org/html/2601.14490v2#S7.SS3 "In 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    4.   [7.4 Grounded OCR and Localization](https://arxiv.org/html/2601.14490v2#S7.SS4 "In 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    5.   [7.5 Benchmarks and Evaluation for OCR and Document Understanding](https://arxiv.org/html/2601.14490v2#S7.SS5 "In 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

8.   [8 Conclusion](https://arxiv.org/html/2601.14490v2#S8 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
9.   [A Interface contract](https://arxiv.org/html/2601.14490v2#A1 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [A.1 Task families & I/O schemas](https://arxiv.org/html/2601.14490v2#A1.SS1 "In Appendix A Interface contract ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [A.2 Geometry and BOX Type](https://arxiv.org/html/2601.14490v2#A1.SS2 "In Appendix A Interface contract ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    3.   [A.3 Layout-Sensitive text2d](https://arxiv.org/html/2601.14490v2#A1.SS3 "In Appendix A Interface contract ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    4.   [A.4 Task-Specific Semantics](https://arxiv.org/html/2601.14490v2#A1.SS4 "In Appendix A Interface contract ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

10.   [B Data](https://arxiv.org/html/2601.14490v2#A2 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [B.1 Real corpora: filtering and normalization](https://arxiv.org/html/2601.14490v2#A2.SS1 "In Appendix B Data ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [B.2 Synthetic corpora: generation pipelines](https://arxiv.org/html/2601.14490v2#A2.SS2 "In Appendix B Data ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    3.   [B.3 Splits and held-out sets](https://arxiv.org/html/2601.14490v2#A2.SS3 "In Appendix B Data ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

11.   [C Training](https://arxiv.org/html/2601.14490v2#A3 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [C.1 Input Preprocessing & Setup](https://arxiv.org/html/2601.14490v2#A3.SS1 "In Appendix C Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [C.2 Hyperparameters](https://arxiv.org/html/2601.14490v2#A3.SS2 "In Appendix C Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    3.   [C.3 System Prompt](https://arxiv.org/html/2601.14490v2#A3.SS3 "In Appendix C Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

12.   [D Evaluation](https://arxiv.org/html/2601.14490v2#A4 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [D.1 Parsing Structured Outputs](https://arxiv.org/html/2601.14490v2#A4.SS1 "In Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [D.2 Metrics](https://arxiv.org/html/2601.14490v2#A4.SS2 "In Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        1.   [D.2.1 Text metrics](https://arxiv.org/html/2601.14490v2#A4.SS2.SSS1 "In D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        2.   [D.2.2 Detection metrics](https://arxiv.org/html/2601.14490v2#A4.SS2.SSS2 "In D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        3.   [D.2.3 End-to-end metrics (detection + recognition)](https://arxiv.org/html/2601.14490v2#A4.SS2.SSS3 "In D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        4.   [D.2.4 Edge cases and invalid predictions](https://arxiv.org/html/2601.14490v2#A4.SS2.SSS4 "In D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

13.   [E Additional Benchmark Details](https://arxiv.org/html/2601.14490v2#A5 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [E.1 Fox Benchmark Details](https://arxiv.org/html/2601.14490v2#A5.SS1 "In Appendix E Additional Benchmark Details ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
    2.   [E.2 OmniDocBench v1.5](https://arxiv.org/html/2601.14490v2#A5.SS2 "In Appendix E Additional Benchmark Details ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

14.   [F Models](https://arxiv.org/html/2601.14490v2#A6 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
15.   [G Additional Results](https://arxiv.org/html/2601.14490v2#A7 "In GutenOCR: A Grounded Vision–Language Front-End for Documents")
    1.   [G.1 Detailed In-Domain Evaluation](https://arxiv.org/html/2601.14490v2#A7.SS1 "In Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        1.   [G.1.1 Reading](https://arxiv.org/html/2601.14490v2#A7.SS1.SSS1 "In G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        2.   [G.1.2 Localized Reading](https://arxiv.org/html/2601.14490v2#A7.SS1.SSS2 "In G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        3.   [G.1.3 Detection](https://arxiv.org/html/2601.14490v2#A7.SS1.SSS3 "In G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")
        4.   [G.1.4 Conditional Detection](https://arxiv.org/html/2601.14490v2#A7.SS1.SSS4 "In G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")

1 Introduction
--------------

Document images remain a primary medium for business transactions, scientific communication, and automated workflows. Optical character recognition (OCR) is therefore the front door for much of the text consumed by large language models (LLMs) and retrieval-augmented generation (RAG) systems: any content that OCR fails to capture is effectively invisible to downstream, text-only systems.

Two main approaches currently shape document OCR. Classical pipelines—with distinct stages for detection, recognition, and layout analysis—offer explicit text grounding and a controllable reading order, but are brittle on complex layouts and difficult to adapt to new domains or tasks[[46](https://arxiv.org/html/2601.14490v2#bib.bib9 "An overview of the tesseract ocr engine"), [10](https://arxiv.org/html/2601.14490v2#bib.bib10 "PaddleOCR 3.0 technical report"), [5](https://arxiv.org/html/2601.14490v2#bib.bib11 "Amazon textractor"), [14](https://arxiv.org/html/2601.14490v2#bib.bib12 "Google cloud vision ocr and document ai ocr")]. “OCR-free” vision–language models (VLMs), by contrast, now dominate many document-understanding benchmarks[[21](https://arxiv.org/html/2601.14490v2#bib.bib2 "OCR-free document understanding transformer"), [58](https://arxiv.org/html/2601.14490v2#bib.bib38 "General ocr theory: towards ocr-2.0 via a unified end-to-end model"), [42](https://arxiv.org/html/2601.14490v2#bib.bib18 "OlmOCR 2: unit test rewards for document ocr"), [51](https://arxiv.org/html/2601.14490v2#bib.bib19 "Infinity parser: layout aware reinforcement learning for scanned document parsing")], scaling to large datasets, handling diverse visual signals, and operating in complex domains (e.g., chemistry, music, mathematics). However, they typically treat text as a latent variable: page-level transcripts are implicit, token-level grounding is at best partial, and reading behavior is controllable only indirectly via prompts. We refer to the OCR component that downstream systems actually interact with as a _grounded OCR front-end_: a model that (i) produces page transcripts, (ii) attaches each token or span to 2D bounding boxes, and (iii) can be prompted to read arbitrary regions on the page.

This lack of an explicit grounded front-end is particularly acute in production settings, where downstream systems need both high-quality text and fine-grained control over _how_ it is read. They require precise local reading, explicit links between tokens and pixels, and representations that can be tailored (e.g., whitespace-sensitive, layout-aware ordering) for extraction, filtering, and RAG. Non-grounded page-to-Markdown outputs make human oversight costly: reviewers must read both the full page and the generated transcript end-to-end, which is slow and error-prone. In contrast, grounded outputs make errors easier to spot and correct: hallucinated content appears as boxes over empty regions, missing text manifests as gaps in box coverage, and misrecognized spans are localized to specific boxes. Grounding therefore directly supports human-in-the-loop verification and active-learning workflows.

Existing OCR-specialized VLMs and end-to-end parsers[[42](https://arxiv.org/html/2601.14490v2#bib.bib18 "OlmOCR 2: unit test rewards for document ocr"), [51](https://arxiv.org/html/2601.14490v2#bib.bib19 "Infinity parser: layout aware reinforcement learning for scanned document parsing"), [59](https://arxiv.org/html/2601.14490v2#bib.bib22 "DeepSeek-ocr: contexts optical compression"), [9](https://arxiv.org/html/2601.14490v2#bib.bib23 "PaddleOCR-vl: boosting multilingual document parsing via a 0.9b ultra-compact vision-language model")] deliver strong page-to-Markdown quality, but are not designed as grounded front-ends: they often couple OCR with task-specific decoding formats, expose limited or unstable token–box alignment, and offer only coarse control over where and how the page is read. When grounded modes are provided, they are frequently tied to bespoke prompt conventions or rigid output schemas that downstream systems must accommodate. Classical OCR engines, in contrast, expose modular, stable APIs for detection, recognition, and layout analysis that can be flexibly composed inside larger business workflows. Rather than forcing legacy systems to retrofit around model-specific formats, we seek VLM-based OCR systems that offer equally versatile, API-like interfaces.

We revisit OCR as a grounded front-end problem and introduce GutenOCR, a VLM-based OCR system trained to behave like a traditional OCR pipeline while retaining the flexibility of contemporary vision–language architectures[[4](https://arxiv.org/html/2601.14490v2#bib.bib16 "Qwen2.5-vl technical report"), [3](https://arxiv.org/html/2601.14490v2#bib.bib17 "Qwen3-vl technical report")]. A single checkpoint supports full-page reading and detection, localized reading, and conditional detection, and can return either plain transcripts or structured line- and paragraph-level outputs with bounding boxes. By releasing the model and training recipe, we aim to establish an open baseline for VLM-based OCR that combines the strengths of classical pipelines with the expressivity and scalability of general-purpose multimodal models, providing a drop-in, human-verifiable front-end for downstream extraction and RAG systems.

In summary, this work makes five contributions:

*   •Unified grounded OCR front-end. We present GutenOCR, a family of 3B and 7B VLM checkpoints that, via prompt-specified input–output schemas, support full-page reading and detection, conditional detection, and localized reading. The models return either linear transcripts or structured line- and paragraph-level outputs with bounding boxes, integrating cleanly with existing business workflows and human-in-the-loop verification pipelines. 
*   •OCR specialization recipe for general-purpose VLMs. We provide a training recipe on a public data mixture that turn Qwen2.5-VL-3B/7B[[4](https://arxiv.org/html/2601.14490v2#bib.bib16 "Qwen2.5-vl technical report")] into grounded OCR-specialized models without modifying the tokenizer, adding adapters, or freezing modules, while supporting long-context page transcripts (up to 8k–16k tokens). 
*   •Metrics and protocol for grounded OCR. We define a metric suite and evaluation protocol that jointly measure text accuracy, detection quality, and page-level fidelity across task families using CER, WER, F1@0.5, mCER@0.5, and CER e2e\text{CER}_{\text{e2e}}. These metrics separate pure recognition errors from localization and reading-order failures, avoiding “good reader, bad paginator” pathologies. 
*   •Empirical analysis across in-domain and external benchmarks. On 10.5K held-out business and scientific pages, GutenOCR-7B substantially improves a composite grounded OCR score, localized-reading CER, and line-detection F1 over its Qwen2.5-VL-7B backbone. On Fox[[29](https://arxiv.org/html/2601.14490v2#bib.bib5 "Focus Anywhere for Fine-grained Multi-page Document Understanding")] and OmniDocBench v1.5[[39](https://arxiv.org/html/2601.14490v2#bib.bib25 "OmniDocBench: benchmarking diverse pdf document parsing with comprehensive annotations")], GutenOCR significantly reduces region- and line-level OCR CER and boosts text-detection recall, while revealing clear failure modes in formula-heavy and color-guided OCR settings (see Figure[1](https://arxiv.org/html/2601.14490v2#S0.F1 "Figure 1 ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")). 
*   •Reproducible open release. We release our training and evaluation code, provide full data provenance (using only publicly available sources), and publish open model weights under a license compatible with the upstream data and model licenses. Our training code can be found at [https://github.com/Roots-Automation/GutenOCR](https://github.com/Roots-Automation/GutenOCR). 

2 GutenOCR Overview
-------------------

Figure 2:  Unified GutenOCR interface. A single vision–language model consumes a page image, optionally conditioned on a text query q q or bounding box b b, and serves multiple OCR-style tasks (reading, detection, conditional detection, localized reading) through prompt-specified input and output schemas. Sub-panels depict each task family: full page detection (top-left), full page reading (top-right), local reading (bottom-right), and conditional detection (bottom-left). Sample page from [[68](https://arxiv.org/html/2601.14490v2#bib.bib60 "The BNIP-2 and Cdc42GAP homology (BCH) domain of p50RhoGAP/Cdc42GAP sequesters RhoA from inactivation by the adjacent GTPase-activating protein domain")]. 

### 2.1 Model Overview

GutenOCR is a family of grounded OCR front-ends as defined in Section[1](https://arxiv.org/html/2601.14490v2#S1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). Each model is a single-checkpoint vision–language system, obtained by fine-tuning Qwen2.5-VL[[4](https://arxiv.org/html/2601.14490v2#bib.bib16 "Qwen2.5-vl technical report")], that exposes classical OCR stages and pointer-like behaviors (for example, “Where is x x in this document?”) via prompts. Conceptually, GutenOCR acts as a thin, API-like layer between page images and downstream systems, exposing a small set of stable OCR primitives (reading, detection, grounding) that can be composed into diverse document workflows.

As depicted in Figure[2](https://arxiv.org/html/2601.14490v2#S2.F2 "Figure 2 ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), each GutenOCR model takes a single document page image as input, optionally augmented with a text query (for conditional detection) or a bounding box (for localized reading), and produces either (i) plain transcripts (text, text2d) or (ii) structured outputs with line- or paragraph-level bounding boxes (lines, paragraphs), depending on the requested mode. All task variants share the same backbone, tokenizer, and prompting interface: the “pipeline” stages of a traditional OCR system (reading, detection, grounding) are exposed as different input–output schemas of a single model, rather than as separate components.

### 2.2 Task Families and Interfaces

Table 1: Canonical task families, inputs, outputs, and prompts.

We expose four task families through a unified, prompt-based interface: full-page reading, full-page detection, conditional detection, and localized reading. We use this four-way taxonomy throughout the paper for both training (Section[3.2](https://arxiv.org/html/2601.14490v2#S3.SS2 "3.2 Training recipe ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")) and evaluation (Section[4.1](https://arxiv.org/html/2601.14490v2#S4.SS1 "4.1 Metrics ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")). Table[1](https://arxiv.org/html/2601.14490v2#S2.T1 "Table 1 ‣ 2.2 Task Families and Interfaces ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") gives canonical input–output schemas and example prompts.

For grounded outputs, we use JSON arrays of objects with keys text and bbox, where bbox is [x 1,y 1,x 2,y 2][x_{1},y_{1},x_{2},y_{2}] in pixel coordinates. For pure detection tasks the output is a JSON array of bbox arrays only. Full-page reading recognizes text over the entire page and can return either linear transcripts (text) or structured outputs (text2d, lines, paragraphs). Full-page detection localizes text or other regions of interest without recognition. Localized reading transcribes user-specified subregions, and conditional detection highlights all instances of a query string.

All outputs of type BOX are axis-aligned bounding boxes in pixel coordinates, represented as [x 1,y 1,x 2,y 2][x_{1},y_{1},x_{2},y_{2}] with x 1<x 2 x_{1}<x_{2}, y 1<y 2 y_{1}<y_{2} in the original image reference frame. We do not predict rotated boxes; rotated or skewed text is represented by the axis-aligned box of its minimal enclosing rectangle. More detailed conventions (e.g., clipping and degenerate boxes) are given in Appendix[A.2](https://arxiv.org/html/2601.14490v2#A1.SS2 "A.2 Geometry and BOX Type ‣ Appendix A Interface contract ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

![Image 2: Refer to caption](https://arxiv.org/html/2601.14490v2/media/38_2010_Article_149.PMC2941081_3-top.png)

Impact of fear on patient’s delay regarding health care seeking behavior                                                   461

seeking behavior ’ or ’ treatment seeking delay ’ or ’ patient      Results
acceptance of health care ’ and ’ fear ’ or ’ anxiety ’ .
   Two reviewers ( TD and JPvD ) independently assessed             Using the first search strategy , 158 articles were found .
the studies that were identified during the screening based         Additional screening based on authors detected another 16
on information obtained from the title and the abstract of          articles , which were not included in the MEDLINE or the

Figure 3:  Example of the layout-sensitive text2d representation. Long runs of spaces encode horizontal alignment (e.g., right-justified page number), while blank lines encode vertical gaps between sections and between the main text and the flow diagram. Page from [[11](https://arxiv.org/html/2601.14490v2#bib.bib59 "The impact of the intensity of fear on patient’s delay regarding health care seeking behavior: a systematic review")]. 

##### Layout-sensitive text2d.

The text2d format is a whitespace-preserving, layout-aware linearization built from line-level boxes and transcripts. We order lines in a 2D reading order and render them into a notional character grid, mapping horizontal gaps to spaces and sufficiently large vertical gaps to blank lines. The resulting text2d string uses only spaces and newline characters to encode 2D layout while remaining a plain-string API for downstream systems (see Figure[3](https://arxiv.org/html/2601.14490v2#S2.F3 "Figure 3 ‣ 2.2 Task Families and Interfaces ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")). The exact construction procedure and its interaction with CER/WER metrics are described in Appendix[A.3](https://arxiv.org/html/2601.14490v2#A1.SS3 "A.3 Layout-Sensitive text2d ‣ Appendix A Interface contract ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

##### Task-specific semantics.

Conditional detection tasks take a query string q q and an image as input and must return bounding boxes for _all_ lines whose normalized text contains q q; if the query does not appear, the expected output is an empty JSON array []. Localized reading tasks take a bounding box and an image as input and require the model to transcribe only the text inside that region. We train both line-level and paragraph-level variants, but for localized reading the API always returns a plain-text string (no boxes). We reuse the labels lines/paragraphs only to indicate the expected granularity of the text, not the JSON structure. Further implementation details are deferred to Appendix[A.4](https://arxiv.org/html/2601.14490v2#A1.SS4 "A.4 Task-Specific Semantics ‣ Appendix A Interface contract ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

3 Data & Training
-----------------

### 3.1 Data curation

We construct the training corpus by combining large-scale real-world document collections with synthetic data targeted at specific grounding behaviors. Our goal is to train a grounded OCR front-end—rather than a general-purpose vision–language model—so we bias the mixture toward scanned documents and synthetic layouts that emphasize line- and paragraph-level geometry, math, and noisy business forms. Table[2](https://arxiv.org/html/2601.14490v2#S3.T2 "Table 2 ‣ Synthetic sources. ‣ 3.1 Data curation ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") summarizes corpus sizes, OCR engines, and available annotation types; Appendix[B](https://arxiv.org/html/2601.14490v2#A2 "Appendix B Data ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") details preprocessing, splits, and sampling.

##### Real sources.

_OCR-IDL (IDL)_[[6](https://arxiv.org/html/2601.14490v2#bib.bib1 "OCR-IDL: OCR Annotations for Industry Document Library Dataset")] covers noisy, heterogeneous business documents (IDs, invoices, claims) with stamps, handwriting, and capture artifacts. _TabMe++ (T++)_[[16](https://arxiv.org/html/2601.14490v2#bib.bib3 "Large Language Models for Page Stream Segmentation")] offers similar content with a different OCR backend and layout distribution. _PubMed-OCR (PMD)_[heidenreich2025pubmedocr] brings long, multi-column scholarly articles with equations, Greek/Latin symbols, figure captions, and references. Training across these sources exposes the model to (i) distinct page organizations (forms, tables, narrative prose), (ii) broad typographic and symbol distributions (small fonts, math, diacritics), and (iii) varied rasterization noise and reading-order conventions. IDL and TabMe++ provide line- and word-level transcripts but no paragraph structure, while PubMed-OCR includes paragraph segmentation in addition to lines and words.

##### Synthetic sources.

We complement real pages with synthetic data that explicitly target grounding for lines and math.

*   •_Grounded L a T e X (GL)._ We mine equation snippets from Wikimedia[[45](https://arxiv.org/html/2601.14490v2#bib.bib6 "Complete list of mathematical expressions in all wikimedia projects, including wikipedia")], normalize them to KaTeX-compatible L a T e X, and render them into single-page PDFs at random positions, scales, and rotations. Each equation is associated with its tight bounding box in the rendered page, providing localized math supervision. 
*   •_SynthDoG grounding (SDG)._ Following prior work[[21](https://arxiv.org/html/2601.14490v2#bib.bib2 "OCR-free document understanding transformer")], we adapt SynthDoG to (i) emit line-level bounding boxes, (ii) sample text from FinePDFs[[22](https://arxiv.org/html/2601.14490v2#bib.bib7 "FinePDFs")], and (iii) use word-sensitive wrapping to avoid mid-word line breaks. These synthetic pages provide dense supervision for line detection and structured reading. 

Table 2:  Dataset statistics and annotation granularity. A checkmark indicates that supervision is available at the corresponding level. 

We reserve 10.5K pages across IDL, TabMe++, and PubMed-OCR for evaluation (Section[5.2](https://arxiv.org/html/2601.14490v2#S5.SS2 "5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")) and train on the remainder. Held-out pages are selected uniformly at random over pages, stratified by source and sequence length. During each training stage, we additionally set aside 2,048 samples as a validation set for early stopping; we halt training when the validation loss saturates. Appendix[B.3](https://arxiv.org/html/2601.14490v2#A2.SS3 "B.3 Splits and held-out sets ‣ Appendix B Data ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") specifies the exact sampling and filtering criteria.

### 3.2 Training recipe

##### Base models.

We fine-tune the public instruction-tuned Qwen2.5-VL-3B and Qwen2.5-VL-7B checkpoints as backbones[[4](https://arxiv.org/html/2601.14490v2#bib.bib16 "Qwen2.5-vl technical report")]. Both support long-context multimodal inputs and are comparable in scale to recent document-focused VLMs, allowing us to study OCR performance as a function of model size under a fixed training recipe. During training, we rasterize each PDF page to a single 72 DPI image and feed it directly to the NaViT‑style Qwen2.5‑VL vision encoder without cropping or tiling (Appendix[C.1](https://arxiv.org/html/2601.14490v2#A3.SS1 "C.1 Input Preprocessing & Setup ‣ Appendix C Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")). Each training example consists of a single page plus a text prompt, with the total sequence length capped according to the stage‑specific limits in Table[3](https://arxiv.org/html/2601.14490v2#S3.T3 "Table 3 ‣ Length-based curriculum. ‣ 3.2 Training recipe ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

##### Optimization and hardware.

We fine‑tune using AdamW[[33](https://arxiv.org/html/2601.14490v2#bib.bib26 "Decoupled weight decay regularization")] on 8×H100 GPUs; see Appendix[C.2](https://arxiv.org/html/2601.14490v2#A3.SS2 "C.2 Hyperparameters ‣ Appendix C Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") for full hyperparameters and implementation details.

##### Prompt variation and image references.

All tasks are prompt-driven. For each (task, input, output) tuple we maintain a bank of prompt templates and sample one uniformly at training time. We also randomize how the image is referenced by sampling from a small set of determiners and nouns, e.g., _“this/that/the provided/the attached”_×\times _“document/image/picture/file/scan”_. Thus prompts such as _“Where is {text} in this document?”_, _“Find occurrences of {text} in the above image and return bounding boxes as JSON.”_, or _“Without returning the text, where are all the LINES in the attached scan?”_ are all seen during training. We observed qualitatively more robust behavior under minor phrasing changes at inference time, while leaving the underlying semantics unchanged.

##### Length-based curriculum.

To stabilize optimization and handle complex layouts at long context, we adopt a curriculum over total sequence length (image prompt plus full-page reading output). We begin with short sequences and gradually extend the maximum length while shifting the dataset mixture, as summarized in Table[3](https://arxiv.org/html/2601.14490v2#S3.T3 "Table 3 ‣ Length-based curriculum. ‣ 3.2 Training recipe ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

Table 3:  Training stages and dataset mixture. SDG = SynthDoG Grounding, GL = Grounded L a T e X, IDL = OCR-IDL, T++ = TabMe++, PMD = PubMed-OCR. Samples are counted by number of pages seen by the model. 

In Stage 1, we train on short sequences (<2,048<2{,}048 tokens) drawn from a mixture of synthetic and real sources: SynthDoG Grounding (SDG), Grounded L a T e X (GL), OCR-IDL (IDL), and TabMe++ (T++). Stage 2 moves to medium-length sequences (2,048 2{,}048–8,192 8{,}192 tokens) and uses only real pages (IDL, TabMe++), dropping synthetic pages and plain page-level transcripts to emphasize structured JSON outputs. Stage 3a keeps the same length range, adds PubMed-OCR (PMD), and introduces paragraph-based reading to refine paragraph structure and long-form page handling. Stage 3b then focuses on the longest contexts (8,192 8{,}192–16,384 16{,}384 tokens) using only PMD, emphasizing multi-column scientific articles and very long transcripts. At each stage we sample uniformly over the task families in Section[2.2](https://arxiv.org/html/2601.14490v2#S2.SS2 "2.2 Task Families and Interfaces ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") that are supported by the available annotations (for example, lines/paragraphs from OCR-IDL and TabMe++, paragraph-level reading and text2d from PubMed-OCR, and detection-only tasks from SynthDoG).

We refer to the resulting checkpoints as GutenOCR-3B,7B Stage 1–3b and evaluate all stages under the grounded OCR metrics of Section[4.1](https://arxiv.org/html/2601.14490v2#S4.SS1 "4.1 Metrics ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

4 Evaluation Setup
------------------

### 4.1 Metrics

We evaluate grounded OCR along three axes: (i) _Text_—character- and word-level errors on string outputs; (ii) _Detection_—localization quality for boxes; and (iii) _End-to-end_—joint quality of box–text pairs and page-level fidelity (including reading order and whitespace). Table[4](https://arxiv.org/html/2601.14490v2#S4.T4 "Table 4 ‣ 4.1 Metrics ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") summarizes which metrics are reported for each task family. Full formal definitions, normalization, and edge-case handling are deferred to Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

Table 4:  Metrics per task family at a glance. Arrows indicate whether lower (↓\downarrow) or higher (↑\uparrow) values are better. 

##### Character- and word-error rates.

For any task that returns plain text, we report character error rate (CER) and word error rate (WER). Both are based on Levenshtein edit distance on lightly normalized strings (Unicode NFKC + whitespace cleanup). Intuitively, CER measures per-character mistakes, while WER is stricter and counts word-level insertions, deletions, and substitutions.

##### Detection metrics.

For detection-style outputs (plain or conditional), we report F1@0.5 and Recall@0.5. Predicted and ground-truth boxes are matched one-to-one using IoU≥0.5\geq 0.5; unmatched predictions count as false positives and unmatched ground-truth boxes as false negatives. The exact matching rule and treatment of corner cases (e.g., pages with no boxes) are specified in Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

##### End-to-end structured reading.

For structured reading tasks that produce text+boxes (lines/paragraphs), we report two text metrics that reuse the matched box set. mCER@0.5 isolates recognition quality given successful localization: we match predicted and ground-truth boxes at IoU≥0.5\geq 0.5, compute CER for each matched text pair, and average over the matched set. Unmatched ground-truth boxes do not affect mCER@0.5 directly (but do count as false negatives in detection recall), cleanly separating “finding the right region” from “reading it correctly.”

CER e2e\text{CER}_{\text{e2e}} measures page-level fidelity. We linearize all predictions and references into page-level strings using a deterministic reading order and a whitespace-preserving layout (as in the text2d output format in Section[2.2](https://arxiv.org/html/2601.14490v2#S2.SS2 "2.2 Task Families and Interfaces ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), then compute CER on these concatenated transcripts. This metric is sensitive to missing or spurious lines, reading-order errors, and layout-sensitive whitespace.

Together, these metrics probe (a) whether models find the right regions, (b) whether they read those regions correctly, and (c) whether the resulting page-level representation preserves reading order and layout-sensitive whitespace.

For multi-task summaries (Section[5.2](https://arxiv.org/html/2601.14490v2#S5.SS2 "5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), we use CER (or CER e2e\text{CER}_{\text{e2e}} for structured reading) as the reading error ϵ\epsilon, convert each into a per-task score 1−ϵ 1-\epsilon, and average these with detection and conditional-detection F1 values to obtain a composite grounded OCR score in [0,1][0,1].

### 4.2 Benchmarks

We evaluate GutenOCR on both in-domain business/scientific pages and public document benchmarks.

##### In-domain documents.

We first evaluate on held-out pages drawn from the same sources used during training (OCR-IDL, TabMe++, PubMed-OCR). For each model we run the full suite of grounded OCR tasks from Section[2.2](https://arxiv.org/html/2601.14490v2#S2.SS2 "2.2 Task Families and Interfaces ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"): full-page reading in multiple output formats (text, text2d, lines), localized reading given a user-specified box, full-page detection, and conditional detection. Metrics follow Table[4](https://arxiv.org/html/2601.14490v2#S4.T4 "Table 4 ‣ 4.1 Metrics ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"): reading tasks are reported as CER/WER errors, while detection tasks are summarized with F1@0.5 and Recall@0.5; structured outputs use mCER@0.5 and CER e2e\text{CER}_{\text{e2e}} for end-to-end quality. Structured predictions are parsed through the shared JSON repair and normalization pipeline in Appendix[D.1](https://arxiv.org/html/2601.14490v2#A4.SS1 "D.1 Parsing Structured Outputs ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") before scoring.

##### Fox.

Fox is a multi-page benchmark that probes a model’s ability to “focus anywhere” on a document via region-level, line-level, and color-guided OCR. We follow the authors’ task definitions and restrict Fox to the four English OCR-style tasks that align with our setting: (i) page OCR, (ii) region-level OCR, (iii) line-level OCR, and (iv) color-guided OCR. For page OCR we report both the reading-order-agnostic soft token F1 (_Page F1_) and the order-sensitive character error rate (_Page CER_); for region, line, and color OCR we report CER only (Table[7](https://arxiv.org/html/2601.14490v2#S5.T7 "Table 7 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")). Additional benchmark details are given in Appendix[E](https://arxiv.org/html/2601.14490v2#A5 "Appendix E Additional Benchmark Details ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

##### OmniDocBench v1.5.

OmniDocBench v1.5 is a diverse PDF benchmark with dense annotations for layout regions, text spans, formulas, and tables across multiple page types. We treat it as an out-of-domain stress test and, restricting to English-only pages, evaluate three behaviors that match our grounded OCR setting: (i) text recognition via CER on cropped text spans, (ii) formula recognition via CDM[[52](https://arxiv.org/html/2601.14490v2#bib.bib58 "Image over text: transforming formula recognition evaluation with character detection matching")] and CER on cropped equations, and (iii) text detection via recall of line-level text boxes. Because OmniDocBench text spans cover only a subset of visible text, we report recall@0.5 (but not precision/F1) for detection under our “detect all readable text” ontology. Full dataset and metric details are deferred to Appendix[E.2](https://arxiv.org/html/2601.14490v2#A5.SS2 "E.2 OmniDocBench v1.5 ‣ Appendix E Additional Benchmark Details ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

5 Results
---------

We evaluate GutenOCR on three settings: in-domain documents, Fox, and OmniDocBench v1.5. Our experiments are designed to answer three questions:

*   •Does GutenOCR improve both reading and grounding over Qwen2.5-VL backbones? 
*   •How does it compare to OCR-specialized and layout-aware models on standard benchmarks? 
*   •How do curriculum stages trade off global reading quality vs fine-grained grounding? 

We first describe the evaluated models (Section[5.1](https://arxiv.org/html/2601.14490v2#S5.SS1 "5.1 Models ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), then in-domain results (Section[5.2](https://arxiv.org/html/2601.14490v2#S5.SS2 "5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), Fox (Section[5.3](https://arxiv.org/html/2601.14490v2#S5.SS3 "5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), OmniDocBench (Section[5.4](https://arxiv.org/html/2601.14490v2#S5.SS4 "5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), and a training-stage ablation (Section[5.5](https://arxiv.org/html/2601.14490v2#S5.SS5 "5.5 Training Stage Ablation ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")).

At a high level, GutenOCR-7B more than doubles the composite grounded OCR score of its Qwen2.5-VL-7B backbone on 10.5K held-out business and scientific pages (0.40→\rightarrow 0.82). On Fox, it substantially improves region- and line-level OCR while sacrificing some page-level linearization and color-guided OCR. On OmniDocBench v1.5, it raises text-detection recall from ≈\approx 0.02 to 0.55–0.62 but slightly degrades formula recognition, especially at 3B. We unpack these trends below.

### 5.1 Models

We consider three groups of models (Table[5](https://arxiv.org/html/2601.14490v2#S5.T5 "Table 5 ‣ 5.1 Models ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")): (i) general-purpose Qwen-based VLMs used via prompting, (ii) OCR-specialized or layout-focused Qwen derivatives, and (iii) our GutenOCR-3B/7B front-ends. Full model descriptions are deferred to Appendix[F](https://arxiv.org/html/2601.14490v2#A6 "Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

Table 5:  Overview of models considered in our evaluation. “Coord. boxes” indicates whether the public interface can emit bounding boxes or coordinates without additional tooling. 

### 5.2 In-Domain

Table 6:  Average in-domain performance on OCR-IDL, TabMe++, and PubMed-OCR across six task families. Reading columns report errors (lower is better, ↓\downarrow); detection columns report F1 scores (higher is better, ↑\uparrow). The composite score averages task-wise values after mapping reading errors ϵ\epsilon to scores 1−ϵ 1-\epsilon. Within each column, bold numbers indicate the best value across all models with a reported score, while underlined numbers indicate the best value within each backbone cohort (e.g., 3B vs. 7B). Entries that are both bold and underlined are best both overall and within their cohort; blank cells denote metrics that were not evaluated for that model. 

We first assess in-domain performance on 10.5K held-out pages drawn from the same real-world sources used in training (OCR-IDL, TabMe++, PubMed-OCR). For each model (and, for GutenOCR, each training stage), we evaluate the six task families from Section[4.1](https://arxiv.org/html/2601.14490v2#S4.SS1 "4.1 Metrics ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"): full-page reading in three output formats (text, text2d, lines), localized reading, full-page detection, and conditional detection. Table[6](https://arxiv.org/html/2601.14490v2#S5.T6 "Table 6 ‣ 5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") reports CER for reading tasks and F1 for detection and conditional detection.

To aggregate across tasks, we convert each reading error ϵ\epsilon into a score 1−ϵ 1-\epsilon and then average these scores with the detection and conditional-detection F1 values, yielding the composite column in Table[6](https://arxiv.org/html/2601.14490v2#S5.T6 "Table 6 ‣ 5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). Under this composite, GutenOCR-3B and GutenOCR-7B (Stage 3a) more than double the scores of their Qwen2.5-VL backbones (from 0.348 to 0.811 and from 0.396 to 0.819, respectively), driven primarily by large gains in localized reading and detection. Unless otherwise noted, we use the Stage 3a checkpoints as the default GutenOCR-3B and GutenOCR-7B models in subsequent experiments.

### 5.3 Fox

Recall from Section[4.2](https://arxiv.org/html/2601.14490v2#S4.SS2 "4.2 Benchmarks ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") that we evaluate on the four English Fox OCR tasks that align with our training objectives: page OCR, region-level OCR, line-level OCR, and color-guided OCR (Table[7](https://arxiv.org/html/2601.14490v2#S5.T7 "Table 7 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")). Page-level performance is reported as both reading-order-agnostic token F1 (_Page F1_) and order-sensitive CER, while the region, line, and color subtasks use CER only (lower is better for CER; higher is better for Page F1).

Table 7:  Results on the English Fox OCR subtasks. _Page F1_ is reading-order agnostic soft token F1 for full-page OCR (higher is better); _Page_ is full-page OCR CER; _Region_ is region-level OCR given a provided box; _Line_ is line-level OCR given a line pointer; and _Color_ is OCR guided only by the color of a box. All entries except _Page F1_ are character error rates (CER; lower is better). Within each column, bold numbers indicate the best value across all models, while underlined numbers indicate the best value within each cohort (3B, 7B, 8B, and Fox/PaddleOCR-VL/DeepSeek-OCR, as separated by horizontal rules). Entries that are both bold and underlined are best both overall and within their cohort. Models with ∗ are copied from the original Fox report; all others are recomputed under a unified prompting setup. 

![Image 3: Refer to caption](https://arxiv.org/html/2601.14490v2/media/en_19_box_annotated.png)GT:This section reports tax revenues from busine…Qwen:Revenue (CER: 0.987)Guten:This section reports tax revenues from busine… (CER: 0.004)(a) Region-level OCR Success![Image 4: Refer to caption](https://arxiv.org/html/2601.14490v2/media/en_92_line_annotated.png)GT:Administrative Apparatus and Functions Qwen:The best way to understand ISIS as a formativ… (CER: 0.988)Guten:Administrative Apparatus and Functions (CER: 0.000)(b) Line Pointer Generalization
![Image 5: Refer to caption](https://arxiv.org/html/2601.14490v2/media/en_69_color.png)GT:December 1988 BAS Meeting Qwen:December 1988 BAS Meeting (CER: 0.000)Guten:[[461, 71, 809, 86], [461, 88, 809, 102], [84… (CER: 0.997)(c) Color OCR Catastrophic Forgetting![Image 6: Refer to caption](https://arxiv.org/html/2601.14490v2/media/en_15_page.png)GT:which could be undertaken for the development…Qwen:National advisory committees on human rights…(CER: 0.574, F1: 0.597)Guten:which could be undertaken for the development…(CER: 0.687, F1: 0.983)(d) Content vs Structure Trade-off

Figure 4:  Qualitative comparison of Qwen2.5-VL-3B and GutenOCR-3B showing complementary strengths and weaknesses. (a) GutenOCR excels at region extraction (CER: 0.004 vs. 0.987). (b) Region training transfers to line pointer tasks (CER: 0.000 vs. 0.988). (c) GutenOCR suffers catastrophic forgetting on color tasks (CER: 0.997 vs. 0.000). (d) Trade-off: GutenOCR achieves higher content F1 (0.983 vs. 0.597) despite worse reading order (CER: 0.687 vs. 0.574) relative to Fox’s reference expectations. 

Fox mixes settings that are close to our training distribution (page- and region-style OCR) with more extrapolative ones (line pointers and color-guided grounding). Page-level results highlight an important distinction between _what_ GutenOCR reads and _how_ it linearizes that content. At 3B, GutenOCR-3B attains the highest Page F1 (0.988), indicating that it reads almost all reference tokens, but its page-level CER is 0.138, much worse than Qwen2.5-VL-3B (0.051) and Nanonets-OCR2-3B (0.026). A similar pattern holds at 7B. The gap between Page F1 and Page CER reflects GutenOCR’s training objective: it is optimized for layout-sensitive text2d and structured line/paragraph JSON, not for Fox’s canonical page-to-Markdown order. Under Page F1 (content only), GutenOCR appears strong; Page CER (content + order) penalizes its layout-driven linearization.

This is consistent with our training objectives. GutenOCR is optimized to produce layout-sensitive text2d outputs and structured line/paragraph JSON, not a single fixed page-to-Markdown format. The model is trained to follow 2D layout cues—columns, tables, headings, and whitespace—when streaming text, which can conflict with the reading order assumed by Fox’s reference markup. Under Page F1 (which ignores order), this yields very high agreement on content; under Page CER (which penalizes reordering and extra text), it appears as relatively weak page OCR despite strong underlying reading ability.

On region-level OCR (_Region_), GutenOCR is best aligned with the intent of Fox. GutenOCR-3B attains a region CER of 0.053, the best value in Table[7](https://arxiv.org/html/2601.14490v2#S5.T7 "Table 7 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") and slightly better than the Fox model itself (0.059), while GutenOCR-7B reaches 0.067. Both represent large gains over the Qwen2.5-VL backbones (0.260 for 3B and 0.163 for 7B), consistent with our focus on grounded, region-aware OCR.

For line-level OCR (_Line_), where Fox provides a pointer to a single line, the Fox model remains strongest overall (0.116 CER), but GutenOCR again substantially improves over its backbones. GutenOCR-3B reduces line CER from 0.817 to 0.240, and GutenOCR-7B from 0.701 to 0.211. Explicit line-pointer prompts do not appear in our training mixture, so this behavior likely reflects transfer from region-level detection and localized reading: once the model learns to find and read arbitrary regions, line pointers become a natural special case.

Color-guided OCR (_Color_) exposes a clear limitation of our current recipe. The Fox model, Qwen2.5-VL-7B, and several OCR-specialized systems leverage color-coded boxes effectively (e.g., 0.064 CER for the Fox model and 0.109 CER for Qwen2.5-VL-7B), whereas both GutenOCR variants perform poorly (0.940 CER for 3B and 0.963 for 7B). Color-conditioned pointers are absent from our training data, and the OCR-focused fine-tuning overwrites the base models’ heuristic ability to interpret these cues, a form of catastrophic forgetting on this narrow but challenging sub-task. Qualitatively, we often observe GutenOCR misreading the instruction as “find the words _red/green/blue_” rather than “read the text in the red/green/blue box.”

GutenOCR explicitly trades some page-level CER on Fox for stronger grounded behavior. It preserves high Page F1 (indicating good reading) while reshaping reading order to follow its layout-sensitive text/text2d training, and it substantially strengthens region- and line-level OCR over the Qwen2.5-VL backbones. We qualitatively illustrate these trade-offs in Figure[4](https://arxiv.org/html/2601.14490v2#S5.F4 "Figure 4 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") for the 3B-parameter model.

### 5.4 OmniDocBench v1.5

Recall from Section[4.2](https://arxiv.org/html/2601.14490v2#S4.SS2 "4.2 Benchmarks ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") that OmniDocBench v1.5[[39](https://arxiv.org/html/2601.14490v2#bib.bib25 "OmniDocBench: benchmarking diverse pdf document parsing with comprehensive annotations")] provides dense annotations for layout regions, text spans, formulas, and tables across nine PDF page types (e.g., books, slides, financial reports, textbooks, exam papers, magazines, academic papers, handwritten notes, and newspapers).1 1 1 See the v1.0→\rightarrow 1.5 changelog in the OmniDocBench supplement for details. The official benchmark is designed around end-to-end markup generation with structure-aware metrics, whereas our production stack targets JSON-style text+box outputs. Rather than retrofitting GutenOCR to OmniDocBench’s canonical markup, we treat it as an out-of-domain stress test for three core capabilities:

1.   1.text recognition (CER on cropped text spans), 
2.   2.formula recognition (CDM and CER on cropped equations), and 
3.   3.text detection (recall of line-level text boxes). 

Throughout, we restrict evaluation to pages whose language tag is purely English.

#### 5.4.1 Text Recognition

Table 8:  Component-level evaluation on the OmniDocBench OCR subset (English-only), grouped by text attributes under the edit-distance metric. All values are CER (lower is better). 

For text recognition we use the OmniDocBench OCR subset, which provides cropped text regions and attributes (language, background color, rotation). We keep only English spans and evaluate character error rate (CER; lower is better) under the same component-level edit-distance metric as the original paper. Following OmniDocBench, we report results at two granularities—full-page OCR and per-sample crops—and further group spans by background type (white, single-color, and multi-color).

Table[8](https://arxiv.org/html/2601.14490v2#S5.T8 "Table 8 ‣ 5.4.1 Text Recognition ‣ 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") summarizes results for the Qwen2.5-VL backbones and their GutenOCR variants. Across both model sizes, OCR-centric fine-tuning slightly increases CER relative to the base models (e.g., from 0.018 to 0.028 page-level CER for Qwen2.5-VL-3B, and from 0.011 to 0.024 for 7B). The degradation is most pronounced on multi-colored backgrounds, where CER more than doubles for both GutenOCR-3B and -7B, while the Qwen2.5-VL baselines remain comparatively robust.

These results complement those from Fox (Section[5.3](https://arxiv.org/html/2601.14490v2#S5.SS3 "5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), where GutenOCR dramatically improves region- and line-level OCR but performs poorly on color-guided pointers. A plausible explanation is domain mismatch: the OmniDocBench OCR subset contains many visually diverse pages (magazines, notes, newspapers, slides) that are under-represented in our training corpus, which focuses on business documents and structured forms, with academic pages added only in the final training phase. Color and background cues are also not modeled explicitly in our current recipe, so the fine-tuning does not inherit the base models’ background robustness on this benchmark.

Table 9:  OmniDocBench OCR subset: CER by page type (English-only; lower is better). 

![Image 7: Refer to caption](https://arxiv.org/html/2601.14490v2/media/omnidocbench-recall.jpg)

Figure 5:  Qualitative OmniDocBench text-detection example. Red boxes denote annotated text spans; blue boxes denote GutenOCR predictions on the same page. Many blue boxes fall on readable text (e.g., table cells and decorative labels) that OmniDocBench does not label as text, so non-overlapping predictions cannot be reliably treated as false positives. This motivates our recall-only evaluation protocol in Section[5.4.2](https://arxiv.org/html/2601.14490v2#S5.SS4.SSS2 "5.4.2 Text Detection ‣ 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 

#### 5.4.2 Text Detection

For text detection, several design choices in OmniDocBench interact with our modeling goals. Text spans are defined at roughly line level and are provided only for a subset of visible text: many visually text-like objects (e.g., table cell content, certain chemical formulas, decorative labels) are either annotated only as part of a Table object or tagged as “Equation Ignore” and excluded from text evaluation. GutenOCR, by contrast, aims to detect _all_ readable text, including text inside tables and equations, and does not attempt to reproduce OmniDocBench’s span-selection heuristics. As illustrated in Figure[5](https://arxiv.org/html/2601.14490v2#S5.F5 "Figure 5 ‣ 5.4.1 Text Recognition ‣ 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), our predictions (blue) cover substantially more text-like regions than the red annotated spans.

Because OmniDocBench’s text annotations cover only a subset of visible text (for example, many table cells and some equations are unlabeled), we cannot reliably treat non-overlapping predictions as false positives. A predicted box that misses an annotated span may be a hallucination or may simply hit unannotated but readable text. We therefore evaluate only recall at IoU≥0.5\geq 0.5, treating the annotated spans as a trusted but incomplete ground truth and asking: when OmniDocBench says there is text here, does our detector cover it?

Table 10:  OmniDocBench layout subset: text detection recall at IoU≥\geq 0.5 (R@0.5) by page type (higher is better). 

Under this recall-only protocol (Table[10](https://arxiv.org/html/2601.14490v2#S5.T10 "Table 10 ‣ 5.4.2 Text Detection ‣ 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), the Qwen2.5-VL backbones almost never produce boxes that align with OmniDocBench’s text spans (R@0.5≈0.02\approx 0.02 for both 3B and 7B). After GutenOCR fine-tuning, recall increases by more than an order of magnitude, reaching 0.620 for GutenOCR-3B and 0.549 for GutenOCR-7B. This is consistent with our design: the GutenOCR curriculum explicitly trains a line-level detection head on diverse business documents, whereas the original Qwen2.5-VL models were never optimized to emit dense text boxes that match an external annotation standard.

We emphasize that these numbers should not be interpreted as full detection quality on OmniDocBench: higher recall here does not imply stronger precision on their ontology, and our models deliberately predict many additional boxes (e.g., table cells, formulas) that the benchmark does not label as text. Rather, OmniDocBench serves as an external check that the detection behavior learned on our in-domain datasets transfers reasonably well to a visually diverse, attribute-rich document collection. Accordingly, we view OmniDocBench text detection as a recall-only stress test rather than a full detector ranking: higher R@0.5 indicates better coverage of annotated spans, but does not reflect precision or behavior on unannotated text.

#### 5.4.3 Formula Recognition

Table 11:  Formula recognition evaluation on the English subset of OmniDocBench. CER is lower-is-better; CDM is higher-is-better. 

OmniDocBench includes a dedicated formula subset with LaTeX ground truth and evaluates models with the Character Detection Matching (CDM) metric[[52](https://arxiv.org/html/2601.14490v2#bib.bib58 "Image over text: transforming formula recognition evaluation with character detection matching")], which measures symbol-level correctness under rendering, together with normalized edit distance. We follow this setup, again filtering to English formulas, and report CDM (higher is better) together with CER in Table[11](https://arxiv.org/html/2601.14490v2#S5.T11 "Table 11 ‣ 5.4.3 Formula Recognition ‣ 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

On formulas, GutenOCR exhibits clear negative transfer relative to its Qwen2.5-VL bases. For the 3B model, CDM drops from 0.936 to 0.866 and CER rises from 0.189 to 0.294; for the 7B model, the degradation is milder but consistent: CDM decreases from 0.935 to 0.927 and CER increases from 0.216 to 0.221.

These results suggest that the current GutenOCR training mixture is effectively math-agnostic (likely exacerbated by dropping LaTeX grounding early on): it substantially improves document OCR (Sections[5.2](https://arxiv.org/html/2601.14490v2#S5.SS2 "5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")–[5.3](https://arxiv.org/html/2601.14490v2#S5.SS3 "5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")) but erodes formula recognition, especially for the 3B model. For equation-heavy use cases, the best-performing checkpoints in our experiments are the un-fine-tuned Qwen2.5-VL backbones, not the GutenOCR variants. Making GutenOCR explicitly math-aware—for example, by incorporating formula-rich supervision similar to the OmniDocBench formula subset—is an important direction for future work.

### 5.5 Training Stage Ablation

To study curriculum trade-offs, we compare GutenOCR checkpoints across training stages on the same held-out in-domain pages. Table[12](https://arxiv.org/html/2601.14490v2#S5.T12 "Table 12 ‣ 5.5 Training Stage Ablation ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") reports averages over OCR-IDL, TabMe++, and PubMed-OCR for each stage, and Figure[6](https://arxiv.org/html/2601.14490v2#S5.F6 "Figure 6 ‣ 5.5 Training Stage Ablation ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") summarizes the corresponding trends in composite score and localized-reading error.

Table 12:  Average in-domain performance on OCR-IDL, TabMe++, and PubMed-OCR across six task families, broken down by training stage. Reading columns report errors (lower is better, ↓\downarrow); detection columns report F1 scores (higher is better, ↑\uparrow). The composite score averages task-wise values after mapping reading errors ϵ\epsilon to scores 1−ϵ 1-\epsilon. Within each column, bold numbers indicate the best value across all models and stages, while underlined numbers indicate the best value within each backbone (3B vs. 7B). Entries that are both bold and underlined are best both overall and within their backbone. 

![Image 8: Refer to caption](https://arxiv.org/html/2601.14490v2/x2.png)

![Image 9: Refer to caption](https://arxiv.org/html/2601.14490v2/x3.png)

Figure 6:  Training-stage ablation summary for composite score (left, higher is better) and localized-reading error (right, lower is better) on OCR-IDL, TabMe++, and PubMed-OCR. The x-axis shows the base model and Stages 1–3; Stage 3a and Stage 3b share the same x-position and are distinguished by line style and marker. 

Relative to the Qwen2.5-VL backbones, GutenOCR yields large and consistent gains across all in-domain tasks. For the 3B model, the best stage (3a) roughly halves full-page reading errors (e.g., text CER 0.508→\rightarrow 0.224), cuts localized-reading error from 0.699 to 0.109, and lifts detection and conditional-detection F1 from 0.135/0.121 to ∼\sim 0.8/0.88, more than doubling the composite (0.348→\rightarrow 0.811). The 7B backbone shows the same pattern: GutenOCR-7B (3a) reduces reading errors by 40–80%, raises detection F1 from 0.111 to 0.787 and conditional detection from 0.285 to 0.882, and increases the composite from 0.396 to 0.819. Thus most of the in-domain improvement comes from the OCR-centric training recipe, not from scaling alone.

After fine-tuning, model-size differences are modest. At their best stages (3a), GutenOCR-7B improves the composite only slightly over GutenOCR-3B (0.819 vs. 0.811). The 7B model consistently achieves lower errors on global reading tasks (text, text2d, lines) and slightly higher overall composite, while the 3B model achieves lower localized-reading error at every stage and slightly higher unconditional detection F1. This trade-off suggests that GutenOCR-3B is a competitive, more efficient choice when local reading and pure detection are prioritized, whereas GutenOCR-7B is preferable when global reading and conditional detection are the main objectives.

Within each backbone, the curriculum stages exhibit clear trends. Stage 1 already captures most of the gains in full-page reading and detection relative to the base VLMs. Stage 2 makes only minor adjustments and is largely dominated by Stage 1 or Stage 3a. Adding Stage 3a mainly sharpens localized reading and conditional detection for both backbones and yields the best composite scores, indicating that the additional curriculum primarily refines grounding rather than further reducing global reading error. By contrast, Stage 3b slightly degrades the composite relative to Stage 3a and does not produce any column-best metrics, consistent with mild over-specialization on the longest PubMed-OCR-style contexts.

Overall, Table[12](https://arxiv.org/html/2601.14490v2#S5.T12 "Table 12 ‣ 5.5 Training Stage Ablation ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") and Figure[6](https://arxiv.org/html/2601.14490v2#S5.F6 "Figure 6 ‣ 5.5 Training Stage Ablation ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") show that GutenOCR turns general-purpose VLMs into strong, grounded OCR systems across in-domain documents, with small but consistent advantages for the 7B backbone and clear stage-wise curriculum trade-offs.

### 5.6 Qualitative Examples

To exemplify how GutenOCR can be used to further improve annotations with a human-in-the-loop, we highlight an example on each real dataset where the 3B parameter model correctly found _more_ lines than were originally annotated by the ground truth OCR engine in Figure[7](https://arxiv.org/html/2601.14490v2#S5.F7 "Figure 7 ‣ 5.6 Qualitative Examples ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

![Image 10: Refer to caption](https://arxiv.org/html/2601.14490v2/media/idl_kyll0135_0028_clean.png)(a) IDL![Image 11: Refer to caption](https://arxiv.org/html/2601.14490v2/media/tabmepp_ffhh0198_0002_clean.png)(b) TabMe++
![Image 12: Refer to caption](https://arxiv.org/html/2601.14490v2/media/pubmed_29.PMC2107773_5_clean.png)(c) PubMed-OCR![Image 13: Refer to caption](https://arxiv.org/html/2601.14490v2/media/pubmed_29.PMC2107773_5_clean-zoom.png)(d) PubMed-OCR (zoom-in)

Figure 7: Qualitative examples of GutenOCR-3B’s lines predictions on test samples. Blue boxes indicate GutenOCR’s prediction versus the ground truth in red. Regions of overlap are purple. Areas of disagreement are immediately obvious (and actionable).

6 Discussion
------------

Taken together, our results suggest that treating OCR as a grounded front-end—rather than as a single page-to-markup conversion—changes both what should be optimized and how OCR outputs are consumed in practice. In particular, when OCR is used as the substrate for downstream retrieval, extraction, and document QA, the most costly failures are often not minor transcription noise but missing regions, unstable reading order, and weak provenance between model outputs and the pixels that support them.

##### Grounded front-ends versus page-only OCR.

Across our in-domain suite, Fox, and OmniDocBench, GutenOCR behaves differently from both its Qwen2.5-VL backbones and contemporary OCR-specialized VLMs. Rather than optimizing a single notion of page-level fidelity, our recipe emphasizes a _grounded front-end_: high recall of text regions, stable line- and paragraph-level outputs, and predictable behavior under localized and conditional reading. This shows up quantitatively in large gains on localized reading and detection metrics (Tables[6](https://arxiv.org/html/2601.14490v2#S5.T6 "Table 6 ‣ 5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")&[7](https://arxiv.org/html/2601.14490v2#S5.T7 "Table 7 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), and qualitatively in cases where GutenOCR recovers legible content that is absent from reference annotations. From a systems perspective, these properties are often as important as small differences in page-level CER: downstream components can tolerate some transcription noise, but they are brittle to missing content, scrambled layout, or non-reproducible pointing behavior that prevents targeted re-reading.

##### Human-in-the-loop verification and control.

Viewed through the lens of human review, GutenOCR is designed to reduce the effort required to decide whether a page is _usable_ for downstream automation. Line- and paragraph-level detection, together with multi-format transcripts (plain text, layout-preserving text, and line-based JSON), let a reviewer quickly answer concrete questions: (i) _Did we cover all the text?_ (recall of boxes over the page), (ii) _Can we reliably re-read a region of interest?_ (localized reading that is stable across prompts), and (iii) _Can we attribute extracted values to evidence?_ (boxes that pinpoint the supporting span). This asymmetric cost profile motivates our bias toward recall and fine-grained grounding: false positives are typically easy to dismiss visually, whereas false negatives force re-scanning the page and make exceptions difficult to triage. In practice, these properties support review tools, exception workflows, and active-learning loops where the goal is not only accurate text but _quickly verifiable_ text and _actionable provenance_. By contrast, page-to-Markdown systems often entangle rendering choices with OCR itself, making isolated errors or ambiguous attributions harder to localize without repeatedly comparing a long transcript to the original page.

##### Interfaces, semantic surface, and comparison to prior work.

A large portion of recent work binds OCR to a single, task-specific output representation: page-to-Markdown/HTML conversion, fixed layout-to-JSON schemas, or document parsing pipelines that produce one canonical “document object” for downstream use. These approaches can be strong end-to-end baselines when the downstream task matches the target representation, but they often provide limited support for (i) alternative reading orders, (ii) region-restricted re-reading, and (iii) fine-grained attribution of answers to the specific spans that support them. In particular, document conversion systems (e.g., those centered on structured markup such as DocTags-like formats[[37](https://arxiv.org/html/2601.14490v2#bib.bib61 "SmolDocling: an ultra-compact vision-language model for end-to-end multi-modal document conversion")]) provide exportable parses that are valuable for rendering and indexing, but they do not by themselves guarantee _evidence-first_ behavior—that is, a stable contract where extracted fields and QA answers can be traced to precise token- or span-level locations on the page.

GutenOCR takes a different position in this design space. It offers a small set of stable, grounded interfaces—full-page reading in multiple formats, localized reading, full-page detection, and conditional detection—all backed by a single checkpoint and a coherent prompting scheme. These interfaces act as a thin, API-like layer between raw pixels and downstream logic: applications consume structured outputs with text and boxes and are free to render or transform them into whatever schema they require (HTML, Markdown, XML, database records) without changing the underlying OCR model. We view this as exposing a broader _semantic surface_—a set of stable OCR primitives that downstream systems can reliably compose—than page-only transcripts, while remaining predictable enough for enterprise integration and human verification.

##### Limitations and open challenges.

Our experiments also reveal the limits of the current recipe. First, specialization for business and scientific documents improves reading and grounding on our in-domain suite and on Fox’s region and line tasks, but can reduce robustness on visually diverse layouts and color-guided cues, and degrades formula recognition on formula-heavy OmniDocBench pages. Second, our outputs are still primarily text- and line-centric: we do not yet explicitly model table structure, math layout, cross-page links, or higher discourse units, even though these are critical for many real workflows (e.g., attributing a financial value to the correct row/column context). Addressing these weaknesses will likely require both a broader training mixture (e.g., math- and table-rich supervision, color- and background-aware tasks) and extended interfaces that surface this structure _without sacrificing_ grounding and controllability. Finally, because our goal is a practical front-end, future work should also characterize efficiency trade-offs (latency/throughput) alongside accuracy and grounding.

##### Toward document holograms.

The preceding points suggest a target beyond OCR alone. We use the term _document hologram_ to describe a persistent, multi-view representation of a document that couples (i) fine-grained grounding between content and pixels (down to spans or tokens), with (ii) learned semantic typing and relations over that grounded content, and (iii) queryable views that support region-restricted inspection and controllable reading orders. Crucially, a document hologram is not merely an export format or parse tree: it is the internal state that enables _evidence-bearing_ responses, where extracted fields and QA answers come with a set of supporting locations (often many-to-many) that a user can directly verify—for example, pointing to the specific cells in a large table that justify a suspected fraudulent amount.

In this sense, GutenOCR should be viewed as a front-end module for document holograms rather than a complete solution. Our results show that a general-purpose VLM can be specialized into a grounded OCR front-end that substantially improves structured reading and detection while preserving localized and pointer-based behaviors useful for evidence retrieval. At the same time, the observed failure modes—math and color sensitivity, table-heavy layouts, and cross-page reasoning—highlight what is still missing from higher hologram layers that model structure and semantics on top of grounded text. We leave the design of these higher layers, and the evaluation protocols that directly test evidential QA and fine-grained provenance, to future work.

7 Related Work
--------------

### 7.1 Classical and Modern OCR Pipelines

Classical OCR systems decompose document understanding into a sequence of stages: image normalization and binarization, text region detection, character- or word-level recognition, and downstream post-processing. Early systems such as Tesseract[[46](https://arxiv.org/html/2601.14490v2#bib.bib9 "An overview of the tesseract ocr engine")] and successors in industrial settings (e.g., PaddleOCR[[10](https://arxiv.org/html/2601.14490v2#bib.bib10 "PaddleOCR 3.0 technical report")] and cloud APIs such as Amazon Textract[[5](https://arxiv.org/html/2601.14490v2#bib.bib11 "Amazon textractor")] and Google Vision OCR[[14](https://arxiv.org/html/2601.14490v2#bib.bib12 "Google cloud vision ocr and document ai ocr")]) largely share this modular structure, even as individual components have shifted from rule-based processing to convolutional detectors and sequence recognizers. Production deployments typically add task-specific logic for page segmentation, tables, forms, and key-value extraction.

Despite their maturity, pipeline OCR systems exhibit well-known limitations on complex documents. First, layout handling can be brittle: multi-column articles, nested tables, stamps, marginalia, and rotated inserts can break reading-order heuristics, scrambling text streams and propagating errors downstream[[57](https://arxiv.org/html/2601.14490v2#bib.bib13 "LayoutReader: Pre-training of Text and Layout for Reading Order Detection"), [64](https://arxiv.org/html/2601.14490v2#bib.bib14 "Reading Order Matters: Information Extraction from Visually-rich Documents by Token Path Prediction")]. Second, the link between text and visual support is often indirect: while many systems expose word- or line-level geometry, programmatic control over reading behavior (alternative reading orders, region-restricted rereading, whitespace-sensitive linearizations, or query-conditioned extraction) typically requires substantial glue logic on top of OCR outputs[[20](https://arxiv.org/html/2601.14490v2#bib.bib15 "Éclair – Extracting Content and Layout with Integrated Reading Order for Documents")]. Finally, hybrid document pipelines frequently combine PDF-native extraction (when embedded text is available) with OCR fallback for scanned or rasterized content; recent work on PDF-centric QA highlights the value of exploiting PDF structure and metadata when available[[44](https://arxiv.org/html/2601.14490v2#bib.bib62 "PDFTriage: question answering over long, structured documents")].

In this work, we adopt the pipeline formulation as our starting point: we aim to preserve the strengths of modular OCR— explicit detection, recognition, and structured outputs—while replacing hand-crafted components with a unified vision–language model. Our GutenOCR system is trained to perform full-page reading, detection, conditional detection, and localized reading within a single VLM interface, behaving like a traditional OCR pipeline from the outside while enabling fine-grained grounding, controllable reading order, and task-specific document representations.

### 7.2 Document Conversion Toolchains and Markup Formats

A complementary line of work targets _document conversion_: converting PDFs and page images into richly structured, LLM-friendly intermediate representations such as Markdown, HTML, or JSON. Docling provides an open-source conversion toolkit that parses multiple document formats into a unified structured representation[[32](https://arxiv.org/html/2601.14490v2#bib.bib63 "Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion")]. Recent compact conversion models such as SmolDocling generate _DocTags_, an XML-like tagged format designed to preserve document structure and element locations while remaining tokenizer-friendly[[37](https://arxiv.org/html/2601.14490v2#bib.bib61 "SmolDocling: an ultra-compact vision-language model for end-to-end multi-modal document conversion")]. IBM’s Granite-Docling-258M similarly targets efficient end-to-end conversion into structured machine-readable formats with tight integration into the Docling toolchain[[49](https://arxiv.org/html/2601.14490v2#bib.bib74 "ibm-granite/granite-docling-258M")]. Other open-source tools (e.g., MinerU) focus on practical PDF-to-Markdown/JSON conversion for scientific and technical documents[[53](https://arxiv.org/html/2601.14490v2#bib.bib66 "MinerU: an open-source solution for precise document content extraction"), [38](https://arxiv.org/html/2601.14490v2#bib.bib65 "MinerU2.5: a decoupled vision-language model for efficient high-resolution document parsing")].

These systems provide strong end-to-end baselines when a downstream application can consume their target schema directly. Our goal is different: rather than committing to a single canonical export format, we emphasize a small set of _OCR primitives as a stable contract_ (detection, reading, localized reading, and conditional detection) that downstream systems can compose into diverse workflows and representations.

### 7.3 Vision–Language Models for Documents

Recent document understanding systems increasingly rely on VLMs that operate on page images. One family consists of _OCR-based_ models such as LayoutLM and successors[[62](https://arxiv.org/html/2601.14490v2#bib.bib27 "LayoutLM: pre-training of text and layout for document image understanding"), [61](https://arxiv.org/html/2601.14490v2#bib.bib28 "LayoutLMv2: multi-modal pre-training for visually-rich document understanding"), [17](https://arxiv.org/html/2601.14490v2#bib.bib29 "LayoutLMv3: pre-training for document ai with unified text and image masking")], DocFormer[[1](https://arxiv.org/html/2601.14490v2#bib.bib30 "DocFormer: end-to-end transformer for document understanding")], DiT[[24](https://arxiv.org/html/2601.14490v2#bib.bib31 "DiT: self-supervised pre-training for document image transformer")], LiLT[[55](https://arxiv.org/html/2601.14490v2#bib.bib32 "LiLT: a simple yet effective language-independent layout transformer for structured document understanding")], and UDOP[[47](https://arxiv.org/html/2601.14490v2#bib.bib8 "Unifying vision, text, and layout for universal document processing")], which consume OCR tokens and bounding boxes. More recently, layout-aware LLM extensions such as DocLLM[[54](https://arxiv.org/html/2601.14490v2#bib.bib67 "DocLLM: a layout-aware generative language model for multimodal document understanding")] and DocLayLLM[[28](https://arxiv.org/html/2601.14490v2#bib.bib68 "DocLayLLM: An Efficient Multi-modal Extension of Large Language Models for Text-rich Document Understanding")] incorporate spatial structure directly into generative LMs, but still assume OCR has produced accurate text and geometry. These approaches achieve strong results on downstream benchmarks (e.g., FUNSD[[18](https://arxiv.org/html/2601.14490v2#bib.bib35 "FUNSD: a dataset for form understanding in noisy scanned documents")], CORD[[40](https://arxiv.org/html/2601.14490v2#bib.bib39 "{cord}: a consolidated receipt dataset for post-{ocr} parsing")], SROIE[[25](https://arxiv.org/html/2601.14490v2#bib.bib36 "ICDAR 2019 competition on scanned receipt ocr and information extraction")], DocVQA[[36](https://arxiv.org/html/2601.14490v2#bib.bib37 "DocVQA: a dataset for vqa on document images")]), but are limited by upstream OCR errors and provide only indirect control over region-restricted reading or query-conditioned localization.

A second family of _OCR-free_ document VLMs operates directly on pixels and emits text or structured markup. Donut[[21](https://arxiv.org/html/2601.14490v2#bib.bib2 "OCR-free document understanding transformer")] is a prominent example; related work on screenshot/document parsing (e.g., Pix2Struct[[23](https://arxiv.org/html/2601.14490v2#bib.bib71 "Pix2Struct: screenshot parsing as pretraining for visual language understanding")]) and scientific document conversion (e.g., Nougat[[7](https://arxiv.org/html/2601.14490v2#bib.bib69 "Nougat: neural optical understanding for academic documents")]) likewise targets page-to-markup generation. Several newer OCR-specialized parsers (e.g., dots.ocr[[26](https://arxiv.org/html/2601.14490v2#bib.bib73 "Dots.ocr: multilingual document layout parsing in a single vision-language model")], DocPedia[[12](https://arxiv.org/html/2601.14490v2#bib.bib70 "DocPedia: Unleashing the Power of Large Multimodal Model in the Frequency Domain for Versatile Document Understanding")]) emphasize faithful conversion and reading order, often producing Markdown/HTML/JSON (sometimes with coordinates) and evaluating primarily via text/markup edit distance.

More recently, several OCR-specialized multimodal models fine-tune VLM backbones for high-fidelity document transcription and parsing. General OCR Theory (GOT) frames OCR as a unified end-to-end “OCR-2.0” model that supports whole-page transcription as well as interactive, region-guided recognition (e.g., via coordinates or colors) and formatted outputs[[58](https://arxiv.org/html/2601.14490v2#bib.bib38 "General ocr theory: towards ocr-2.0 via a unified end-to-end model")]. Other systems use reinforcement learning or verifiable reward signals to improve structural fidelity and reading order in page-to-text/markup conversion, including olmOCR[[42](https://arxiv.org/html/2601.14490v2#bib.bib18 "OlmOCR 2: unit test rewards for document ocr")] and Infinity-Parser[[51](https://arxiv.org/html/2601.14490v2#bib.bib19 "Infinity parser: layout aware reinforcement learning for scanned document parsing")]. These models provide strong end-to-end conversion baselines, but they typically expose a primary canonical output representation (plain text or markup) rather than a small set of schema-stable OCR primitives spanning pure detection, localized re-reading, and string-conditioned search.

In parallel, general-purpose vision foundation models (e.g., Florence-2[[60](https://arxiv.org/html/2601.14490v2#bib.bib72 "Florence-2: advancing a unified representation for a variety of vision tasks")], Granite Vision[[48](https://arxiv.org/html/2601.14490v2#bib.bib64 "Granite vision: a lightweight, open-source multimodal model for enterprise intelligence")], Qwen2.5-VL/Qwen3-VL[[4](https://arxiv.org/html/2601.14490v2#bib.bib16 "Qwen2.5-vl technical report"), [3](https://arxiv.org/html/2601.14490v2#bib.bib17 "Qwen3-vl technical report")], InternVL variants[[8](https://arxiv.org/html/2601.14490v2#bib.bib46 "Internvl: scaling up vision foundation models and aligning for generic visual-linguistic tasks"), [69](https://arxiv.org/html/2601.14490v2#bib.bib41 "Internvl3: exploring advanced training and test-time recipes for open-source multimodal models"), [56](https://arxiv.org/html/2601.14490v2#bib.bib40 "InternVL3.5: advancing open-source multimodal models in versatility, reasoning, and efficiency")]) can perform document QA, captioning, and OCR-like behaviors when suitably prompted. However, their interfaces and training objectives are typically optimized for broad multimodal instruction following rather than a well-specified OCR API contract, and coordinate outputs are often exposed through ad-hoc formats.

Our work takes a different stance: we explicitly retrain a general-purpose VLM backbone as a grounded OCR front-end with task schemas that mirror a classical OCR pipeline (full-page reading, detection, localized reading, and conditional detection). The primary product is a set of structured text+box outputs and prompt-selectable behaviors, rather than QA answers or a single canonical document linearization.

### 7.4 Grounded OCR and Localization

Before the rise of VLMs, grounded OCR was studied through _text spotting_ systems that jointly detect and recognize text (e.g., EAST[[67](https://arxiv.org/html/2601.14490v2#bib.bib48 "EAST: an efficient and accurate scene text detector")], CTPN[[50](https://arxiv.org/html/2601.14490v2#bib.bib51 "Detecting text in natural image with connectionist text proposal network")], FOTS[[31](https://arxiv.org/html/2601.14490v2#bib.bib49 "FOTS: fast oriented text spotting with a unified network")], Mask TextSpotter[[34](https://arxiv.org/html/2601.14490v2#bib.bib50 "Mask textspotter: an end-to-end trainable neural network for spotting text with arbitrary shapes")]). These models provide explicit box–text pairs, but are often tuned for scene text and do not naturally support document abstractions or language-driven queries.

More recently, work on reading order and layout-aware extraction (e.g., LayoutReader[[57](https://arxiv.org/html/2601.14490v2#bib.bib13 "LayoutReader: Pre-training of Text and Layout for Reading Order Detection")], Reading Order Matters[[64](https://arxiv.org/html/2601.14490v2#bib.bib14 "Reading Order Matters: Information Extraction from Visually-rich Documents by Token Path Prediction")], éclair[[20](https://arxiv.org/html/2601.14490v2#bib.bib15 "Éclair – Extracting Content and Layout with Integrated Reading Order for Documents")]) assumes OCR tokens exist. Meanwhile, phrase-grounding models (e.g., MDETR[[19](https://arxiv.org/html/2601.14490v2#bib.bib52 "MDETR – modulated detection for end-to-end multi-modal understanding")], GLIP[[27](https://arxiv.org/html/2601.14490v2#bib.bib53 "Grounded language-image pre-training"), [65](https://arxiv.org/html/2601.14490v2#bib.bib54 "GLIPv2: unifying localization and vision-language understanding")], Grounding DINO[[30](https://arxiv.org/html/2601.14490v2#bib.bib33 "Grounding dino: marrying dino with grounded pre-training for open-set object detection"), [43](https://arxiv.org/html/2601.14490v2#bib.bib34 "Grounding dino 1.5: advance the \"edge\" of open-set object detection")]) align language with regions; document-focused tasks appear in benchmarks such as Fox[[29](https://arxiv.org/html/2601.14490v2#bib.bib5 "Focus Anywhere for Fine-grained Multi-page Document Understanding")]. Foundation models such as Florence-2 expose OCR and region-level prompting as part of a unified multi-task interface[[60](https://arxiv.org/html/2601.14490v2#bib.bib72 "Florence-2: advancing a unified representation for a variety of vision tasks")].

Several OCR-focused VLM parsers annotate outputs with coordinates or support prompted localization (e.g., dots.ocr[[26](https://arxiv.org/html/2601.14490v2#bib.bib73 "Dots.ocr: multilingual document layout parsing in a single vision-language model")], SmolDocling/DocTags[[37](https://arxiv.org/html/2601.14490v2#bib.bib61 "SmolDocling: an ultra-compact vision-language model for end-to-end multi-modal document conversion")]). However, these interfaces are typically optimized for end-to-end conversion rather than a single checkpoint that unifies _pure detection_, _localized rereading_, and _string-conditioned search_ under a stable, schema-driven API with standardized conditional-localization metrics.

GutenOCR can be viewed as a generalization of text spotting and phrase grounding to a unified, VLM-based OCR interface: one checkpoint supports (i) full-page detection, (ii) full-page structured reading, (iii) localized reading given a user box, and (iv) conditional detection given a query string, all expressed through prompt-selectable schemas.

### 7.5 Benchmarks and Evaluation for OCR and Document Understanding

Classical OCR evaluation has been driven by ICDAR-style benchmarks for scene text and document text recognition, which typically separate detection and recognition. Detection is measured with IoU-based precision, recall, and F1 at one or more thresholds; recognition quality is reported as character error rate (CER), word accuracy, or normalized edit distance on isolated words, lines, or cropped regions. End-to-end text spotting benchmarks often combine localization and recognition through matching-based protocols (e.g., end-to-end F-score/Hmean), and more fine-grained schemes such as CLEval score character-level correctness while handling split/merge cases in detection[[2](https://arxiv.org/html/2601.14490v2#bib.bib75 "CLEval: character-level evaluation for text detection and recognition tasks")].

Document understanding benchmarks broaden the focus from text recognition to classification and extraction. Datasets such as RVL-CDIP[[15](https://arxiv.org/html/2601.14490v2#bib.bib56 "Evaluation of deep convolutional nets for document image classification and retrieval")], FUNSD[[18](https://arxiv.org/html/2601.14490v2#bib.bib35 "FUNSD: a dataset for form understanding in noisy scanned documents")], CORD[[40](https://arxiv.org/html/2601.14490v2#bib.bib39 "{cord}: a consolidated receipt dataset for post-{ocr} parsing")], SROIE[[25](https://arxiv.org/html/2601.14490v2#bib.bib36 "ICDAR 2019 competition on scanned receipt ocr and information extraction")], and DocVQA[[36](https://arxiv.org/html/2601.14490v2#bib.bib37 "DocVQA: a dataset for vqa on document images")] evaluate document image classification, form understanding, key-value extraction, and question answering, typically assuming access to an external OCR system. In these settings, OCR quality is a hidden variable: models are judged on downstream task accuracy, and errors stemming from misrecognition, mis-localization, or poor reading order are entangled.

More recent benchmarks have started to evaluate document parsing and grounding more directly. Fox[[29](https://arxiv.org/html/2601.14490v2#bib.bib5 "Focus Anywhere for Fine-grained Multi-page Document Understanding")] introduces multi-page, fine-grained tasks such as region-level OCR, line-level OCR, and color-guided OCR, using CER on cropped regions as the primary metric. OmniDocBench v1.5[[39](https://arxiv.org/html/2601.14490v2#bib.bib25 "OmniDocBench: benchmarking diverse pdf document parsing with comprehensive annotations")] provides dense annotations for layout regions, text spans, formulas, and tables across a diverse set of page types; it reports component-level edit distance for text, CDM and edit distance for formulas[[52](https://arxiv.org/html/2601.14490v2#bib.bib58 "Image over text: transforming formula recognition evaluation with character detection matching")], and structure-aware metrics such as TEDS for tables[[66](https://arxiv.org/html/2601.14490v2#bib.bib57 "Image-based table recognition: data, model, and evaluation")]. These benchmarks substantially raise the bar on the diversity and richness of evaluation. At the same time, they are primarily organized around either component-wise parsing fidelity (text/formula/table/reading-order modules) or end-to-end markup correctness under a particular canonicalization[[39](https://arxiv.org/html/2601.14490v2#bib.bib25 "OmniDocBench: benchmarking diverse pdf document parsing with comprehensive annotations")]. They do not directly evaluate interactive OCR primitives such as region-restricted re-reading or string-conditioned conditional detection under a unified, schema-driven contract. Recent OCR benchmarks for large multimodal models also evaluate OCR across multiple task tracks (e.g., multilingual reading, document parsing, and key information extraction), highlighting common failure modes such as grounding errors and repetition hallucinations[[63](https://arxiv.org/html/2601.14490v2#bib.bib76 "CC-ocr: a comprehensive and challenging ocr benchmark for evaluating large multimodal models in literacy"), [13](https://arxiv.org/html/2601.14490v2#bib.bib77 "OCRBench v2: an improved benchmark for evaluating large multimodal models on visual text localization and reasoning")].

Our evaluation protocol builds on these traditions but targets _grounded OCR_ as a first-class objective. Following Section[4.1](https://arxiv.org/html/2601.14490v2#S4.SS1 "4.1 Metrics ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), we measure: (i) text accuracy via a balanced CER and WER on whole-page transcripts and localized crops; (ii) detection quality via F1@0.5 and Recall@0.5 over axis-aligned boxes; and (iii) end-to-end quality via CERe2e and mCER@0.5 on aligned box–text pairs, which together disentangle localization errors (missing, spurious, or mis-ordered boxes) from recognition errors within correctly localized regions. Unlike prior work that reports either text-only metrics or IoU-only metrics, this metric set evaluates (a) whether models find the right regions, (b) whether they read those regions correctly, and (c) whether the resulting page-level representation preserves reading order and layout-sensitive whitespace. In this sense, our metrics are an explicit evolution of classical OCR and text-spotting criteria toward the grounded, layout-aware document representations that document-hologram systems require.

8 Conclusion
------------

GutenOCR recasts OCR as a grounded front-end problem, training a single vision–language checkpoint to support full-page reading, detection, localized reading, and conditional detection through a unified prompt interface. Across in-domain business and scientific documents, Fox, and OmniDocBench v1.5, it substantially improves structured reading and detection over Qwen2.5-VL backbones and several OCR-specialized baselines, while revealing clear failure modes in formula-heavy and color-guided settings. These results suggest that explicit grounding and controllable reading are as important as page-level transcripts for downstream document systems and point toward richer “document hologram” representations that we leave for future work.

References
----------

*   [1]S. Appalaraju, B. Jasani, B. U. Kota, Y. Xie, and R. Manmatha (2021-10)DocFormer: end-to-end transformer for document understanding. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV),  pp.993–1003. Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [2]Y. Baek, D. Nam, S. Park, J. Lee, S. Shin, J. Baek, C. Y. Lee, and H. Lee (2020)CLEval: character-level evaluation for text detection and recognition tasks. arXiv preprint arXiv:2006.06244. Cited by: [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p1.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [3]S. Bai, Y. Cai, R. Chen, K. Chen, X. Chen, Z. Cheng, L. Deng, W. Ding, C. Gao, C. Ge, W. Ge, Z. Guo, Q. Huang, J. Huang, F. Huang, B. Hui, S. Jiang, Z. Li, M. Li, M. Li, K. Li, Z. Lin, J. Lin, X. Liu, J. Liu, C. Liu, Y. Liu, D. Liu, S. Liu, D. Lu, R. Luo, C. Lv, R. Men, L. Meng, X. Ren, X. Ren, S. Song, Y. Sun, J. Tang, J. Tu, J. Wan, P. Wang, P. Wang, Q. Wang, Y. Wang, T. Xie, Y. Xu, H. Xu, J. Xu, Z. Yang, M. Yang, J. Yang, A. Yang, B. Yu, F. Zhang, H. Zhang, X. Zhang, B. Zheng, H. Zhong, J. Zhou, F. Zhou, J. Zhou, Y. Zhu, and K. Zhu (2025)Qwen3-vl technical report. External Links: 2511.21631, [Link](https://arxiv.org/abs/2511.21631)Cited by: [Appendix F](https://arxiv.org/html/2601.14490v2#A6.SS0.SSS0.Px2.p1.1 "Qwen3-VL ‣ Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p5.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p4.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [4]S. Bai, K. Chen, X. Liu, J. Wang, W. Ge, S. Song, K. Dang, P. Wang, S. Wang, J. Tang, H. Zhong, Y. Zhu, M. Yang, Z. Li, J. Wan, P. Wang, W. Ding, Z. Fu, Y. Xu, J. Ye, X. Zhang, T. Xie, Z. Cheng, H. Zhang, Z. Yang, H. Xu, and J. Lin (2025)Qwen2.5-vl technical report. External Links: 2502.13923, [Link](https://arxiv.org/abs/2502.13923)Cited by: [Appendix F](https://arxiv.org/html/2601.14490v2#A6.SS0.SSS0.Px1.p1.1 "Qwen2.5-VL ‣ Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [2nd item](https://arxiv.org/html/2601.14490v2#S1.I1.i2.p1.1 "In 1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p5.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§2.1](https://arxiv.org/html/2601.14490v2#S2.SS1.p1.1 "2.1 Model Overview ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§3.2](https://arxiv.org/html/2601.14490v2#S3.SS2.SSS0.Px1.p1.1 "Base models. ‣ 3.2 Training recipe ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p4.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [5]E. Belval, T. Delteil, M. Schade, and S. Radhakrishna (2025)Amazon textractor. Note: [https://aws-samples.github.io/amazon-textract-textractor/](https://aws-samples.github.io/amazon-textract-textractor/)External Links: [Link](https://aws-samples.github.io/amazon-textract-textractor/)Cited by: [§1](https://arxiv.org/html/2601.14490v2#S1.p2.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.1](https://arxiv.org/html/2601.14490v2#S7.SS1.p1.1 "7.1 Classical and Modern OCR Pipelines ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [6]A. F. Biten, R. Tito, L. Gomez, E. Valveny, and D. Karatzas (2022-02)OCR-IDL: OCR Annotations for Industry Document Library Dataset. arXiv. External Links: 2202.12985, [Document](https://dx.doi.org/10.48550/arXiv.2202.12985)Cited by: [§3.1](https://arxiv.org/html/2601.14490v2#S3.SS1.SSS0.Px1.p1.1 "Real sources. ‣ 3.1 Data curation ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [7]L. Blecher, G. Cucurull, T. Scialom, and R. Stojnic (2023)Nougat: neural optical understanding for academic documents. External Links: 2308.13418, [Link](https://arxiv.org/abs/2308.13418)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p2.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [8]Z. Chen, J. Wu, W. Wang, W. Su, G. Chen, S. Xing, M. Zhong, Q. Zhang, X. Zhu, L. Lu, et al. (2024)Internvl: scaling up vision foundation models and aligning for generic visual-linguistic tasks. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition,  pp.24185–24198. Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p4.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [9]C. Cui, T. Sun, S. Liang, T. Gao, Z. Zhang, J. Liu, X. Wang, C. Zhou, H. Liu, M. Lin, Y. Zhang, Y. Zhang, H. Zheng, J. Zhang, J. Zhang, Y. Liu, D. Yu, and Y. Ma (2025)PaddleOCR-vl: boosting multilingual document parsing via a 0.9b ultra-compact vision-language model. External Links: 2510.14528, [Link](https://arxiv.org/abs/2510.14528)Cited by: [Appendix F](https://arxiv.org/html/2601.14490v2#A6.SS0.SSS0.Px8.p1.1 "PaddleOCR-VL ‣ Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p4.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [10]C. Cui, T. Sun, M. Lin, T. Gao, Y. Zhang, J. Liu, X. Wang, Z. Zhang, C. Zhou, H. Liu, Y. Zhang, W. Lv, K. Huang, Y. Zhang, J. Zhang, J. Zhang, Y. Liu, D. Yu, and Y. Ma (2025)PaddleOCR 3.0 technical report. External Links: 2507.05595, [Link](https://arxiv.org/abs/2507.05595)Cited by: [§1](https://arxiv.org/html/2601.14490v2#S1.p2.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.1](https://arxiv.org/html/2601.14490v2#S7.SS1.p1.1 "7.1 Classical and Modern OCR Pipelines ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [11]T. Dubayova, J. P. van Dijk, I. Nagyova, J. Rosenberger, E. Havlikova, Z. Gdovinova, B. Middel, and J. W. Groothoff (2010-10)The impact of the intensity of fear on patient’s delay regarding health care seeking behavior: a systematic review. International Journal of Public Health 55 (5),  pp.459–468. Note: Epub 2010 May 14 External Links: [Document](https://dx.doi.org/10.1007/s00038-010-0149-0)Cited by: [Figure 3](https://arxiv.org/html/2601.14490v2#S2.F3 "In 2.2 Task Families and Interfaces ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [12]H. Feng, Q. Liu, H. Liu, J. Tang, W. Zhou, H. Li, and C. Huang (2024-11)DocPedia: Unleashing the Power of Large Multimodal Model in the Frequency Domain for Versatile Document Understanding. arXiv. External Links: 2311.11810, [Document](https://dx.doi.org/10.48550/arXiv.2311.11810)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p2.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [13]L. Fu, Z. Kuang, J. Song, M. Huang, B. Yang, Y. Li, L. Zhu, Q. Luo, X. Wang, H. Lu, Z. Li, G. Tang, B. Shan, C. Lin, Q. Liu, B. Wu, H. Feng, H. Liu, C. Huang, J. Tang, W. Chen, L. Jin, Y. Liu, and X. Bai (2025)OCRBench v2: an improved benchmark for evaluating large multimodal models on visual text localization and reasoning. External Links: 2501.00321, [Link](https://arxiv.org/abs/2501.00321)Cited by: [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p3.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [14]Google Cloud (2025)Google cloud vision ocr and document ai ocr. Google LLC. Note: Optical Character Recognition (OCR) services provided by Google Cloud, including Cloud Vision API and Document AI.[https://cloud.google.com/use-cases/ocr](https://cloud.google.com/use-cases/ocr)External Links: [Link](https://cloud.google.com/use-cases/ocr)Cited by: [§1](https://arxiv.org/html/2601.14490v2#S1.p2.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.1](https://arxiv.org/html/2601.14490v2#S7.SS1.p1.1 "7.1 Classical and Modern OCR Pipelines ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [15]A. W. Harley, A. Ufkes, and K. G. Derpanis (2015)Evaluation of deep convolutional nets for document image classification and retrieval. In International Conference on Document Analysis and Recognition (ICDAR), Cited by: [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p2.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [16]H. Heidenreich, R. Dalvi, R. Mukku, N. Verma, and N. Pičuljan (2024-08)Large Language Models for Page Stream Segmentation. arXiv. External Links: 2408.11981, [Document](https://dx.doi.org/10.48550/arXiv.2408.11981)Cited by: [§3.1](https://arxiv.org/html/2601.14490v2#S3.SS1.SSS0.Px1.p1.1 "Real sources. ‣ 3.1 Data curation ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [17]Y. Huang, T. Lv, L. Cui, Y. Lu, and F. Wei (2022)LayoutLMv3: pre-training for document ai with unified text and image masking. In Proceedings of the 30th ACM International Conference on Multimedia, MM ’22, New York, NY, USA,  pp.4083–4091. External Links: ISBN 9781450392037, [Link](https://doi.org/10.1145/3503161.3548112), [Document](https://dx.doi.org/10.1145/3503161.3548112)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [18]G. Jaume, H. K. Ekenel, and J. Thiran (2019)FUNSD: a dataset for form understanding in noisy scanned documents. In 2019 International Conference on Document Analysis and Recognition Workshops (ICDARW),  pp.1–6. Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p2.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [19]A. Kamath, M. Singh, Y. LeCun, G. Synnaeve, I. Misra, and N. Carion (2021)MDETR – modulated detection for end-to-end multi-modal understanding. External Links: 2104.12763, [Link](https://arxiv.org/abs/2104.12763)Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [20]I. Karmanov, A. S. Deshmukh, L. Voegtle, P. Fischer, K. Chumachenko, T. Roman, J. Seppänen, J. Parmar, J. Jennings, A. Tao, and K. Sapra (2025-02)Éclair – Extracting Content and Layout with Integrated Reading Order for Documents. arXiv. External Links: 2502.04223, [Document](https://dx.doi.org/10.48550/arXiv.2502.04223)Cited by: [§7.1](https://arxiv.org/html/2601.14490v2#S7.SS1.p2.1 "7.1 Classical and Modern OCR Pipelines ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [21]G. Kim, T. Hong, M. Yim, J. Nam, J. Park, J. Yim, W. Hwang, S. Yun, D. Han, and S. Park (2022)OCR-free document understanding transformer. In European Conference on Computer Vision (ECCV), Cited by: [§B.2](https://arxiv.org/html/2601.14490v2#A2.SS2.SSS0.Px2.p1.1 "SynthDoG grounding (SDG). ‣ B.2 Synthetic corpora: generation pipelines ‣ Appendix B Data ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p2.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [2nd item](https://arxiv.org/html/2601.14490v2#S3.I1.i2.p1.1 "In Synthetic sources. ‣ 3.1 Data curation ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p2.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [22]H. Kydlíček, G. Penedo, and L. von Werra (2025)FinePDFs. Hugging Face. Note: [https://huggingface.co/datasets/HuggingFaceFW/finepdfs](https://huggingface.co/datasets/HuggingFaceFW/finepdfs)Cited by: [item 1](https://arxiv.org/html/2601.14490v2#A2.I3.i1.p1.1 "In SynthDoG grounding (SDG). ‣ B.2 Synthetic corpora: generation pipelines ‣ Appendix B Data ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [2nd item](https://arxiv.org/html/2601.14490v2#S3.I1.i2.p1.1 "In Synthetic sources. ‣ 3.1 Data curation ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [23]K. Lee, M. Joshi, I. Turc, H. Hu, F. Liu, J. Eisenschlos, U. Khandelwal, P. Shaw, M. Chang, and K. Toutanova (2023)Pix2Struct: screenshot parsing as pretraining for visual language understanding. External Links: 2210.03347, [Link](https://arxiv.org/abs/2210.03347)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p2.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [24]J. Li, Y. Xu, T. Lv, L. Cui, C. Zhang, and F. Wei (2022)DiT: self-supervised pre-training for document image transformer. In Proceedings of the 30th ACM International Conference on Multimedia, MM ’22, New York, NY, USA,  pp.3530–3539. External Links: ISBN 9781450392037, [Link](https://doi.org/10.1145/3503161.3547911), [Document](https://dx.doi.org/10.1145/3503161.3547911)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [25]M. Li, Y. Deng, Y. Guan, W. Xu, P. Zhang, J. Zhang, X. Zhu, Y. He, H. Li, Y. Jiang, et al. (2019)ICDAR 2019 competition on scanned receipt ocr and information extraction. In 2019 International Conference on Document Analysis and Recognition (ICDAR),  pp.1594–1599. External Links: [Document](https://dx.doi.org/10.1109/ICDAR.2019.00266)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p2.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [26]Y. Li, G. Yang, H. Liu, B. Wang, and C. Zhang (2025)Dots.ocr: multilingual document layout parsing in a single vision-language model. External Links: 2512.02498, [Link](https://arxiv.org/abs/2512.02498)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p2.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p3.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [27]L. H. Li*, P. Zhang*, H. Zhang*, J. Yang, C. Li, Y. Zhong, L. Wang, L. Yuan, L. Zhang, J. Hwang, K. Chang, and J. Gao (2022)Grounded language-image pre-training. In CVPR, Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [28]W. Liao, J. Wang, H. Li, C. Wang, J. Huang, and L. Jin DocLayLLM: An Efficient Multi-modal Extension of Large Language Models for Text-rich Document Understanding. Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [29]C. Liu, H. Wei, J. Chen, L. Kong, Z. Ge, Z. Zhu, L. Zhao, J. Sun, C. Han, and X. Zhang (2024-05)Focus Anywhere for Fine-grained Multi-page Document Understanding. arXiv. External Links: 2405.14295, [Document](https://dx.doi.org/10.48550/arXiv.2405.14295)Cited by: [§E.1](https://arxiv.org/html/2601.14490v2#A5.SS1.SSS0.Px1.p1.1 "Tasks and filtering. ‣ E.1 Fox Benchmark Details ‣ Appendix E Additional Benchmark Details ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [4th item](https://arxiv.org/html/2601.14490v2#S1.I1.i4.p1.1 "In 1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p3.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [30]S. Liu, Z. Zeng, T. Ren, F. Li, H. Zhang, J. Yang, Q. Jiang, C. Li, J. Yang, H. Su, J. Zhu, and L. Zhang (2024)Grounding dino: marrying dino with grounded pre-training for open-set object detection. External Links: 2303.05499, [Link](https://arxiv.org/abs/2303.05499)Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [31]X. Liu, D. Liang, S. Yan, D. Chen, Y. Qiao, and J. Yan (2018-06)FOTS: fast oriented text spotting with a unified network. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p1.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [32]N. Livathinos, C. Auer, M. Lysak, A. Nassar, M. Dolfi, P. Vagenas, C. B. Ramis, M. Omenetti, K. Dinkla, Y. Kim, S. Gupta, R. T. de Lima, V. Weber, L. Morin, I. Meijer, V. Kuropiatnyk, and P. Staar (2025-02)Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion. In AAAI Conference on Artificial Intelligence, Cited by: [§7.2](https://arxiv.org/html/2601.14490v2#S7.SS2.p1.1 "7.2 Document Conversion Toolchains and Markup Formats ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [33]I. Loshchilov and F. Hutter (2019)Decoupled weight decay regularization. External Links: 1711.05101, [Link](https://arxiv.org/abs/1711.05101)Cited by: [§C.2](https://arxiv.org/html/2601.14490v2#A3.SS2.p1.4 "C.2 Hyperparameters ‣ Appendix C Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§3.2](https://arxiv.org/html/2601.14490v2#S3.SS2.SSS0.Px2.p1.1 "Optimization and hardware. ‣ 3.2 Training recipe ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [34]P. Lyu, M. Liao, C. Yao, W. Wu, and X. Bai (2018-09)Mask textspotter: an end-to-end trainable neural network for spotting text with arbitrary shapes. In Proceedings of the European Conference on Computer Vision (ECCV), Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p1.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [35]S. Mandal, A. Talewar, S. Thakuria, P. Ahuja, and P. Juvatkar (2025)Nanonets-ocr2: a model for transforming documents into structured markdown with intelligent content recognition and semantic tagging. Cited by: [Appendix F](https://arxiv.org/html/2601.14490v2#A6.SS0.SSS0.Px3.p1.1 "Nanonets OCR2-3B ‣ Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [36]M. Mathew, D. Karatzas, R. Manmatha, and C. V. Jawahar (2020)DocVQA: a dataset for vqa on document images. 2021 IEEE Winter Conference on Applications of Computer Vision (WACV),  pp.2199–2208. External Links: [Link](https://api.semanticscholar.org/CorpusID:220280200)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p2.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [37]A. Nassar, A. Marafioti, M. Omenetti, M. Lysak, N. Livathinos, C. Auer, L. Morin, R. T. de Lima, Y. Kim, A. S. Gurbuz, M. Dolfi, M. Farré, and P. W. J. Staar (2025)SmolDocling: an ultra-compact vision-language model for end-to-end multi-modal document conversion. External Links: 2503.11576, [Link](https://arxiv.org/abs/2503.11576)Cited by: [§6](https://arxiv.org/html/2601.14490v2#S6.SS0.SSS0.Px3.p1.1 "Interfaces, semantic surface, and comparison to prior work. ‣ 6 Discussion ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.2](https://arxiv.org/html/2601.14490v2#S7.SS2.p1.1 "7.2 Document Conversion Toolchains and Markup Formats ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p3.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [38]J. Niu, Z. Liu, Z. Gu, B. Wang, L. Ouyang, Z. Zhao, T. Chu, T. He, F. Wu, Q. Zhang, Z. Jin, G. Liang, R. Zhang, W. Zhang, Y. Qu, Z. Ren, Y. Sun, Y. Zheng, D. Ma, Z. Tang, B. Niu, Z. Miao, H. Dong, S. Qian, J. Zhang, J. Chen, F. Wang, X. Zhao, L. Wei, W. Li, S. Wang, R. Xu, Y. Cao, L. Chen, Q. Wu, H. Gu, L. Lu, K. Wang, D. Lin, G. Shen, X. Zhou, L. Zhang, Y. Zang, X. Dong, J. Wang, B. Zhang, L. Bai, P. Chu, W. Li, J. Wu, L. Wu, Z. Li, G. Wang, Z. Tu, C. Xu, K. Chen, Y. Qiao, B. Zhou, D. Lin, W. Zhang, and C. He (2025)MinerU2.5: a decoupled vision-language model for efficient high-resolution document parsing. External Links: 2509.22186, [Link](https://arxiv.org/abs/2509.22186)Cited by: [§7.2](https://arxiv.org/html/2601.14490v2#S7.SS2.p1.1 "7.2 Document Conversion Toolchains and Markup Formats ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [39]L. Ouyang, Y. Qu, H. Zhou, J. Zhu, R. Zhang, Q. Lin, B. Wang, Z. Zhao, M. Jiang, X. Zhao, J. Shi, F. Wu, P. Chu, M. Liu, Z. Li, C. Xu, B. Zhang, B. Shi, Z. Tu, and C. He (2025)OmniDocBench: benchmarking diverse pdf document parsing with comprehensive annotations. External Links: 2412.07626, [Link](https://arxiv.org/abs/2412.07626)Cited by: [§E.2](https://arxiv.org/html/2601.14490v2#A5.SS2.p1.1 "E.2 OmniDocBench v1.5 ‣ Appendix E Additional Benchmark Details ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [4th item](https://arxiv.org/html/2601.14490v2#S1.I1.i4.p1.1 "In 1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§5.4](https://arxiv.org/html/2601.14490v2#S5.SS4.p1.1 "5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p3.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [40]S. Park, S. Shin, B. Lee, J. Lee, J. Surh, M. Seo, and H. Lee (2019){cord}: a consolidated receipt dataset for post-{ocr} parsing. In Workshop on Document Intelligence at NeurIPS 2019, External Links: [Link](https://openreview.net/forum?id=SJl3z659UH)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p2.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [41]V. Paruchuri (2025-10)Introducing our newest model: chandra. External Links: [Link](https://www.datalab.to/blog/introducing-chandra)Cited by: [Appendix F](https://arxiv.org/html/2601.14490v2#A6.SS0.SSS0.Px6.p1.1 "Chandra OCR ‣ Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [42]J. Poznanski, L. Soldaini, and K. Lo (2025)OlmOCR 2: unit test rewards for document ocr. External Links: 2510.19817, [Link](https://arxiv.org/abs/2510.19817)Cited by: [Appendix F](https://arxiv.org/html/2601.14490v2#A6.SS0.SSS0.Px4.p1.1 "olmOCR 2 ‣ Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p2.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p4.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p3.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [43]T. Ren, Q. Jiang, S. Liu, Z. Zeng, W. Liu, H. Gao, H. Huang, Z. Ma, X. Jiang, Y. Chen, Y. Xiong, H. Zhang, F. Li, P. Tang, K. Yu, and L. Zhang (2024)Grounding dino 1.5: advance the "edge" of open-set object detection. External Links: 2405.10300, [Link](https://arxiv.org/abs/2405.10300)Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [44]J. Saad-Falcon, J. Barrow, A. Siu, A. Nenkova, D. S. Yoon, R. A. Rossi, and F. Dernoncourt (2023)PDFTriage: question answering over long, structured documents. External Links: 2309.08872, [Link](https://arxiv.org/abs/2309.08872)Cited by: [§7.1](https://arxiv.org/html/2601.14490v2#S7.SS1.p2.1 "7.1 Classical and Modern OCR Pipelines ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [45]M. Schubotz (2025-04)Complete list of mathematical expressions in all wikimedia projects, including wikipedia. Zenodo. Note: [https://doi.org/10.5281/zenodo.15162182](https://doi.org/10.5281/zenodo.15162182)External Links: [Document](https://dx.doi.org/10.5281/zenodo.15162182), [Link](https://doi.org/10.5281/zenodo.15162182)Cited by: [item 1](https://arxiv.org/html/2601.14490v2#A2.I2.i1.p1.1 "In Grounded LaTeX (GL). ‣ B.2 Synthetic corpora: generation pipelines ‣ Appendix B Data ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [1st item](https://arxiv.org/html/2601.14490v2#S3.I1.i1.p1.1 "In Synthetic sources. ‣ 3.1 Data curation ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [46]R. Smith (2007)An overview of the tesseract ocr engine. In ICDAR ’07: Proceedings of the Ninth International Conference on Document Analysis and Recognition, Washington, DC, USA,  pp.629–633. External Links: [Link](https://storage.googleapis.com/pub-tools-public-publication-data/pdf/33418.pdf), ISBN 0-7695-2822-8 Cited by: [§1](https://arxiv.org/html/2601.14490v2#S1.p2.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.1](https://arxiv.org/html/2601.14490v2#S7.SS1.p1.1 "7.1 Classical and Modern OCR Pipelines ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [47]Z. Tang, Z. Yang, G. Wang, Y. Fang, Y. Liu, C. Zhu, M. Zeng, C. Zhang, and M. Bansal (2023)Unifying vision, text, and layout for universal document processing. In 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), Vol. ,  pp.19254–19264. External Links: [Document](https://dx.doi.org/10.1109/CVPR52729.2023.01845)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [48]G. V. Team, L. Karlinsky, A. Arbelle, A. Daniels, A. Nassar, A. Alfassi, B. Wu, E. Schwartz, D. Joshi, J. Kondic, N. Shabtay, P. Li, R. Herzig, S. Abedin, S. Perek, S. Harary, U. Barzelay, A. R. Goldfarb, A. Oliva, B. Wieles, B. Bhattacharjee, B. Huang, C. Auer, D. Gutfreund, D. Beymer, D. Wood, H. Kuehne, J. Hansen, J. Shtok, K. Wong, L. A. Bathen, M. Mishra, M. Lysak, M. Dolfi, M. Yurochkin, N. Livathinos, N. Harel, O. Azulai, O. Naparstek, R. T. de Lima, R. Panda, S. Doveh, S. Gupta, S. Das, S. Zawad, Y. Kim, Z. He, A. Brooks, G. Goodhart, A. Govindjee, D. Leist, I. Ibrahim, A. Soffer, D. Cox, K. Soule, L. Lastras, N. Desai, S. Ofek-koifman, S. Raghavan, T. Syeda-Mahmood, P. Staar, T. Drory, and R. Feris (2025)Granite vision: a lightweight, open-source multimodal model for enterprise intelligence. External Links: 2502.09927, [Link](https://arxiv.org/abs/2502.09927)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p4.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [49]I. G. team (2025)ibm-granite/granite-docling-258M. Hugging Face. Note: [https://huggingface.co/ibm-granite/granite-docling-258M](https://huggingface.co/ibm-granite/granite-docling-258M)Cited by: [§7.2](https://arxiv.org/html/2601.14490v2#S7.SS2.p1.1 "7.2 Document Conversion Toolchains and Markup Formats ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [50]Z. Tian, W. Huang, T. He, P. He, and Y. Qiao (2016)Detecting text in natural image with connectionist text proposal network. In European conference on computer vision,  pp.56–72. Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p1.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [51]B. Wang, B. Wu, W. Li, M. Fang, Z. Huang, J. Huang, H. Wang, Y. Liang, L. Chen, W. Chu, and Y. Qi (2025)Infinity parser: layout aware reinforcement learning for scanned document parsing. External Links: 2506.03197, [Link](https://arxiv.org/abs/2506.03197)Cited by: [Appendix F](https://arxiv.org/html/2601.14490v2#A6.SS0.SSS0.Px5.p1.1 "Infinity-Parser-7B ‣ Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p2.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p4.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p3.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [52]B. Wang, F. Wu, L. Ouyang, Z. Gu, R. Zhang, R. Xia, B. Zhang, and C. He (2025)Image over text: transforming formula recognition evaluation with character detection matching. External Links: 2409.03643, [Link](https://arxiv.org/abs/2409.03643)Cited by: [§E.2](https://arxiv.org/html/2601.14490v2#A5.SS2.SSS0.Px2.p1.1 "Formula recognition subset. ‣ E.2 OmniDocBench v1.5 ‣ Appendix E Additional Benchmark Details ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§4.2](https://arxiv.org/html/2601.14490v2#S4.SS2.SSS0.Px3.p1.1 "OmniDocBench v1.5. ‣ 4.2 Benchmarks ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§5.4.3](https://arxiv.org/html/2601.14490v2#S5.SS4.SSS3.p1.1 "5.4.3 Formula Recognition ‣ 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p3.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [53]B. Wang, C. Xu, X. Zhao, L. Ouyang, F. Wu, Z. Zhao, R. Xu, K. Liu, Y. Qu, F. Shang, B. Zhang, L. Wei, Z. Sui, W. Li, B. Shi, Y. Qiao, D. Lin, and C. He (2024)MinerU: an open-source solution for precise document content extraction. External Links: 2409.18839, [Link](https://arxiv.org/abs/2409.18839)Cited by: [§7.2](https://arxiv.org/html/2601.14490v2#S7.SS2.p1.1 "7.2 Document Conversion Toolchains and Markup Formats ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [54]D. Wang, N. Raman, M. Sibue, Z. Ma, P. Babkin, S. Kaur, Y. Pei, A. Nourbakhsh, and X. Liu (2024-08)DocLLM: a layout-aware generative language model for multimodal document understanding. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), L. Ku, A. Martins, and V. Srikumar (Eds.), Bangkok, Thailand,  pp.8529–8548. External Links: [Link](https://aclanthology.org/2024.acl-long.463/), [Document](https://dx.doi.org/10.18653/v1/2024.acl-long.463)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [55]J. Wang, L. Jin, and K. Ding (2022-05)LiLT: a simple yet effective language-independent layout transformer for structured document understanding. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), S. Muresan, P. Nakov, and A. Villavicencio (Eds.), Dublin, Ireland,  pp.7747–7757. External Links: [Link](https://aclanthology.org/2022.acl-long.534/), [Document](https://dx.doi.org/10.18653/v1/2022.acl-long.534)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [56]W. Wang, Z. Gao, L. Gu, H. Pu, L. Cui, X. Wei, Z. Liu, L. Jing, S. Ye, J. Shao, et al. (2025)InternVL3.5: advancing open-source multimodal models in versatility, reasoning, and efficiency. arXiv preprint arXiv:2508.18265. Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p4.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [57]Z. Wang, Y. Xu, L. Cui, J. Shang, and F. Wei (2021-11)LayoutReader: Pre-training of Text and Layout for Reading Order Detection. In Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing, M. Moens, X. Huang, L. Specia, and S. W. Yih (Eds.), Online and Punta Cana, Dominican Republic,  pp.4735–4744. External Links: [Document](https://dx.doi.org/10.18653/v1/2021.emnlp-main.389)Cited by: [§7.1](https://arxiv.org/html/2601.14490v2#S7.SS1.p2.1 "7.1 Classical and Modern OCR Pipelines ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [58]H. Wei, C. Liu, J. Chen, J. Wang, L. Kong, Y. Xu, Z. Ge, L. Zhao, J. Sun, Y. Peng, C. Han, and X. Zhang (2024)General ocr theory: towards ocr-2.0 via a unified end-to-end model. External Links: 2409.01704, [Link](https://arxiv.org/abs/2409.01704)Cited by: [§1](https://arxiv.org/html/2601.14490v2#S1.p2.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p3.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [59]H. Wei, Y. Sun, and Y. Li (2025)DeepSeek-ocr: contexts optical compression. External Links: 2510.18234, [Link](https://arxiv.org/abs/2510.18234)Cited by: [Appendix F](https://arxiv.org/html/2601.14490v2#A6.SS0.SSS0.Px7.p1.1 "DeepSeek-OCR ‣ Appendix F Models ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§1](https://arxiv.org/html/2601.14490v2#S1.p4.1 "1 Introduction ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [60]B. Xiao, H. Wu, W. Xu, X. Dai, H. Hu, Y. Lu, M. Zeng, C. Liu, and L. Yuan (2023)Florence-2: advancing a unified representation for a variety of vision tasks. External Links: 2311.06242, [Link](https://arxiv.org/abs/2311.06242)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p4.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [61]Y. Xu, Y. Xu, T. Lv, L. Cui, F. Wei, G. Wang, Y. Lu, D. Florencio, C. Zhang, W. Che, M. Zhang, and L. Zhou (2021-08)LayoutLMv2: multi-modal pre-training for visually-rich document understanding. In Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers), C. Zong, F. Xia, W. Li, and R. Navigli (Eds.), Online,  pp.2579–2591. External Links: [Link](https://aclanthology.org/2021.acl-long.201/), [Document](https://dx.doi.org/10.18653/v1/2021.acl-long.201)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [62]Y. Xu, M. Li, L. Cui, S. Huang, F. Wei, and M. Zhou (2020-08)LayoutLM: pre-training of text and layout for document image understanding. In Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, KDD ’20,  pp.1192–1200. External Links: [Link](http://dx.doi.org/10.1145/3394486.3403172), [Document](https://dx.doi.org/10.1145/3394486.3403172)Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p1.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [63]Z. Yang, J. Tang, Z. Li, P. Wang, J. Wan, H. Zhong, X. Liu, M. Yang, P. Wang, S. Bai, L. Jin, and J. Lin (2024)CC-ocr: a comprehensive and challenging ocr benchmark for evaluating large multimodal models in literacy. External Links: 2412.02210, [Link](https://arxiv.org/abs/2412.02210)Cited by: [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p3.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [64]C. Zhang, Y. Guo, Y. Tu, H. Chen, J. Tang, H. Zhu, Q. Zhang, and T. Gui (2023-12)Reading Order Matters: Information Extraction from Visually-rich Documents by Token Path Prediction. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, H. Bouamor, J. Pino, and K. Bali (Eds.), Singapore,  pp.13716–13730. External Links: [Document](https://dx.doi.org/10.18653/v1/2023.emnlp-main.846)Cited by: [§7.1](https://arxiv.org/html/2601.14490v2#S7.SS1.p2.1 "7.1 Classical and Modern OCR Pipelines ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [65]H. Zhang, P. Zhang, X. Hu, Y. Chen, L. H. Li, X. Dai, L. Wang, L. Yuan, J. Hwang, and J. Gao (2022)GLIPv2: unifying localization and vision-language understanding. arXiv preprint arXiv:2206.05836. Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p2.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [66]X. Zhong, E. ShafieiBavani, and A. J. Yepes (2020)Image-based table recognition: data, model, and evaluation. External Links: 1911.10683, [Link](https://arxiv.org/abs/1911.10683)Cited by: [§7.5](https://arxiv.org/html/2601.14490v2#S7.SS5.p3.1 "7.5 Benchmarks and Evaluation for OCR and Document Understanding ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [67]X. Zhou, C. Yao, H. Wen, Y. Wang, S. Zhou, W. He, and J. Liang (2017-07)EAST: an efficient and accurate scene text detector. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), Cited by: [§7.4](https://arxiv.org/html/2601.14490v2#S7.SS4.p1.1 "7.4 Grounded OCR and Localization ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [68]Y. T. Zhou, L. L. Chew, S. C. Lin, and B. C. Low (2010-09)The BNIP-2 and Cdc42GAP homology (BCH) domain of p50RhoGAP/Cdc42GAP sequesters RhoA from inactivation by the adjacent GTPase-activating protein domain. Molecular Biology of the Cell 21 (18),  pp.3232–3246. Note: Epub 2010 Jul 21 External Links: [Document](https://dx.doi.org/10.1091/mbc.E09-05-0408)Cited by: [Figure 2](https://arxiv.org/html/2601.14490v2#S2.F2 "In 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 
*   [69]J. Zhu, W. Wang, Z. Chen, Z. Liu, S. Ye, L. Gu, H. Tian, Y. Duan, W. Su, J. Shao, et al. (2025)Internvl3: exploring advanced training and test-time recipes for open-source multimodal models. arXiv preprint arXiv:2504.10479. Cited by: [§7.3](https://arxiv.org/html/2601.14490v2#S7.SS3.p4.1 "7.3 Vision–Language Models for Documents ‣ 7 Related Work ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). 

Appendix A Interface contract
-----------------------------

### A.1 Task families & I/O schemas

For each task family in Section[2.2](https://arxiv.org/html/2601.14490v2#S2.SS2 "2.2 Task Families and Interfaces ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), we parameterize the interface by a _task type_ (reading, detection, conditional_detection, localized_reading), an _input type_ (image only, image + query string, image + bounding box), and an _output type_ (text, text2d, lines, paragraphs, BOX).

At training time we maintain a small bank of prompt templates for each (task, input, output) triple and sample one uniformly, to encourage robustness to minor paraphrases. Below we list representative templates for each family; in all cases {FORMAT} is replaced with one of the output types (text, text2d, lines, paragraphs):

##### Full-page reading.

*   •“Read all text in the provided document and return the result as {FORMAT}.” 
*   •“Transcribe the text from this page. Use the {FORMAT} format described above.” 
*   •“Without adding explanations, output only the {FORMAT} representation of the page.” 

##### Full-page detection.

*   •“Without returning any text, detect all LINES in this document and output their bounding boxes as a JSON array.” 
*   •“Locate all PARAGRAPHS in the image and return a JSON array of boxes [x 1,y 1,x 2,y 2][x_{1},y_{1},x_{2},y_{2}]. Do not include text.” 
*   •“Detect all math regions in the page and return their bounding boxes as JSON.” 

##### Conditional detection.

*   •“Where does the exact string "{q}" appear in this document? Return a JSON array of bounding boxes for all matching lines.” 
*   •“Search for "{q}" in the page and output [x 1,y 1,x 2,y 2][x_{1},y_{1},x_{2},y_{2}] boxes for each line that contains it. If there are no matches, return [].” 

##### Localized reading.

*   •“What text appears inside the region [x 1,y 1,x 2,y 2][x_{1},y_{1},x_{2},y_{2}] of this page? Return only the recognized text.” 
*   •“Read the text inside the specified box and output a lines or paragraphs string, without JSON or extra commentary.” 

During training, we also randomize the noun used to refer to the image (e.g., “document”, “image”, “page”, “scan”) and simple determiners (e.g., “this”, “that”, “the attached”, “the provided”). We qualitatively found that this light prompt augmentation improves robustness to prompt phrasing at inference time while keeping the semantics of the task fixed.

### A.2 Geometry and BOX Type

All grounded outputs ultimately reduce to axis-aligned bounding boxes in the coordinate system of the input image.

##### Coordinate system.

We use integer pixel coordinates with origin at the top-left corner of the rasterized page. A bounding box is represented as

[x 1,y 1,x 2,y 2][x_{1},y_{1},x_{2},y_{2}]

with x 1<x 2 x_{1}<x_{2} and y 1<y 2 y_{1}<y_{2}. Here x x increases to the right and y y increases downward.

##### Axis-aligned boxes only.

We do not predict rotated boxes. Rotated or skewed text is represented by the axis-aligned bounding box of its minimal enclosing rectangle. This choice simplifies evaluation and downstream consumption.

##### Clipping and degeneracies.

During post-processing we apply the following normalizations to both predictions and references:

*   •Clip all coordinates to the closed interval [0,W]×[0,H][0,W]\times[0,H], where W W and H H are the image width and height in pixels. 
*   •Discard degenerate boxes with non-positive width or height (i.e., x 1≥x 2 x_{1}\geq x_{2} or y 1≥y 2 y_{1}\geq y_{2}). 

These steps ensure that all boxes used for evaluation have strictly positive area and lie within the image bounds.

##### Grounded output schema.

Whenever an output type is grounded and includes text, we use JSON arrays of objects of the form

{"text": <string>, "bbox": [x1, y1, x2, y2]}

For pure detection tasks, where no text is required, the output is a JSON array of bounding boxes only:

[
  [x1, y1, x2, y2],
  [x1, y1, x2, y2],
  ...
]

We apply a tolerant JSON-repair step before evaluation and treat irreparable outputs as invalid; see Appendix[D.1](https://arxiv.org/html/2601.14490v2#A4.SS1 "D.1 Parsing Structured Outputs ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") for details.

### A.3 Layout-Sensitive text2d

The text2d representation is designed to encode 2D layout using only spaces and newline characters while remaining a plain string. It is constructed from line-level grounded outputs of the form {"text","bbox"} as follows.

##### Preprocessing.

We begin with a set of line predictions {(t^i,b i)}i=1 N\{(\hat{t}_{i},b_{i})\}_{i=1}^{N}, where b i=[x 1,i,y 1,i,x 2,i,y 2,i]b_{i}=[x_{1,i},y_{1,i},x_{2,i},y_{2,i}]. We discard boxes with non-positive width or height and clip all remaining boxes to the image bounds. We then compute simple global statistics (e.g., median line height and a crude character density in characters per pixel) that are used to approximate how many fixed-width “character cells” fit in a typical line.

##### Line ordering.

We sort lines according to a 2D reading order: first by the vertical position of the line center (top-to-bottom), then by the horizontal position of the left edge (left-to-right) within each row. This ordering approximates a natural reading order across multi-column layouts and figures.

##### Mapping to a notional grid.

We conceptually render lines into a notional character grid. For each ordered line, we:

*   •Map the absolute horizontal position of its left edge to a character column index using the estimated character density. 
*   •Insert spaces to account for horizontal gaps between consecutive lines on the same row (e.g., to right-justify page numbers or align columns). 
*   •Emit the normalized line text norm⁡(t^i)\operatorname{norm}\!\left(\hat{t}_{i}\right) at the corresponding columns. 

Vertical gaps between consecutive lines are measured in pixels using the distance between their vertical centers. If this gap exceeds a threshold proportional to the estimated line height, we insert one or more blank lines in the output. In practice we cap the number of inserted blank lines to a small maximum to avoid pathological vertical expansion.

##### Final string.

After all lines have been placed, we obtain a 2D grid with characters and spaces. We trim trailing spaces on each row and convert the grid to a single string by joining rows with newline characters. The result is a text2d string that:

*   •preserves relative horizontal alignment via runs of spaces, 
*   •preserves vertical structure via explicit blank lines, and 
*   •can be consumed by downstream systems as a plain-text API. 

During evaluation, we preserve whitespace in text2d so that layout-sensitive differences (e.g., scrambled columns or collapsed vertical gaps) are reflected in the error.

### A.4 Task-Specific Semantics

##### Conditional detection.

Each conditional-detection example consists of a page image, a query string q q, and a target set of line-level boxes. To construct the target, we take the reference line transcripts and apply the same normalization norm⁡(⋅)\operatorname{norm}\!\left(\cdot\right) used for text metrics (Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), including Unicode NFKC normalization, trimming of leading/trailing whitespace, and collapsing of internal whitespace runs. We apply norm⁡(⋅)\operatorname{norm}\!\left(\cdot\right) to both the query and each line transcript and mark a line as a hit if the normalized query appears as a case-sensitive substring of the normalized line.

If the query does not appear on the page, the ground truth set is empty and the expected model output is an empty JSON array [] with no additional commentary. When a query appears multiple times on the same line, we treat that as a single target box; if it appears on multiple lines, all corresponding line boxes are included in the target set. During evaluation we compare predicted and reference boxes with IoU-based matching at a threshold of 0.5; unmatched predicted boxes are false positives and unmatched reference boxes are false negatives.

##### Localized reading.

For localized reading, the input consists of a page image and a bounding box b=[x 1,y 1,x 2,y 2]b=[x_{1},y_{1},x_{2},y_{2}] in pixel coordinates. The model is expected to transcribe only the text inside b b. We train both line-level and paragraph-level variants, but in both cases the _output_ is treated as non-grounded: the model returns a single plain-text string rather than a JSON array of {"text","bbox"} objects.

To construct training labels, we intersect b b with the reference line- or paragraph-level boxes and concatenate the transcripts of blocks whose overlap with b b exceeds an IoU threshold (we use 0.5 in all experiments). The resulting string is used as the target transcript for that localized reading example. At evaluation time, we compute CER and WER between the model output and this target string, again using norm⁡(⋅)\operatorname{norm}\!\left(\cdot\right) to normalize whitespace and Unicode variants.

##### Full-page reading and detection.

For full-page reading tasks, the model receives only the page image and is prompted to produce either:

*   •a linear transcript (text), 
*   •a whitespace-preserving transcript (text2d), or 
*   •a structured array of line-/paragraph-level objects (lines/paragraphs). 

Structured predictions are parsed through the JSON repair and normalization pipeline described in Appendix[D.1](https://arxiv.org/html/2601.14490v2#A4.SS1 "D.1 Parsing Structured Outputs ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). Invalid or irreparable outputs are treated as failures and assigned maximal error according to Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

For full-page detection, the model receives only the page image and must output a JSON array of bounding boxes that cover all lines or paragraphs of interest, without transcripts. Supervision and metrics follow the detection protocol in Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), using IoU-based matching at threshold 0.5.

Appendix B Data
---------------

### B.1 Real corpora: filtering and normalization

For OCR-IDL and PubMed-OCR we start from document-level PDFs and associated OCR outputs provided by each source. We apply a common preprocessing pipeline to obtain page images and normalized ground-truth annotations.

All PDFs are rasterized to single-page RGB images at 72 dpi. TabMe++ was rasterized in the initial construction of TabMe and is used as is.

##### Text normalization.

For each available transcript (paragraph-, line-, or word-level) we apply the same normalization operator norm⁡(⋅)\operatorname{norm}\!\left(\cdot\right) used for text metrics (Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), including:

*   •Unicode NFKC normalization, 
*   •conversion of platform-specific quotes, dashes, and bullets to canonical ASCII or Unicode codepoints, 
*   •trimming of leading/trailing whitespace, and 
*   •collapsing of internal whitespace runs into a single space. 

This produces consistent supervision across datasets and aligns training-time targets with evaluation-time normalization.

##### Geometry unification.

All datasets provide boxes in pixel coordinates, but differ in conventions (e.g., half-open vs. closed intervals, one-based vs. zero-based indices). We map all coordinates to the axis-aligned [x 1,y 1,x 2,y 2][x_{1},y_{1},x_{2},y_{2}] convention from Section[2.2](https://arxiv.org/html/2601.14490v2#S2.SS2 "2.2 Task Families and Interfaces ‣ 2 GutenOCR Overview ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), clip to image bounds, and discard degenerate boxes with non-positive width or height.

### B.2 Synthetic corpora: generation pipelines

##### Grounded L a T e X (GL).

The GL corpus is designed to provide highly localized supervision for mathematical expressions.

1.   1.Equation mining. We extract raw L a T e X fragments from Wikimedia dumps following [[45](https://arxiv.org/html/2601.14490v2#bib.bib6 "Complete list of mathematical expressions in all wikimedia projects, including wikipedia")]. 
2.   2.

Rendering. For each equation we create a blank page and render the equation at a randomly sampled:

    *   •rotation angle, and 
    *   •sub-pixel position on the page. 

##### SynthDoG grounding (SDG).

The SDG corpus adapts SynthDoG[[21](https://arxiv.org/html/2601.14490v2#bib.bib2 "OCR-free document understanding transformer")] to better match our line-centric grounding objectives.

1.   1.Text source. We draw raw text snippets from FinePDFs[[22](https://arxiv.org/html/2601.14490v2#bib.bib7 "FinePDFs")], sampling both narrative and transactional content. Snippets are truncated to at most a few hundred characters to keep synthetic pages compact. 
2.   2.Layout generation. We use SynthDoG’s layout engine to place text blocks, but modify the line-breaking logic to be word-aware: line breaks are only inserted at whitespace, and hyphenation is disabled. This avoids mid-word splits that complicate line-level supervision. 
3.   3.Line-level supervision. We instrument the generator to emit line-level bounding boxes and transcripts directly, in addition to any word-level boxes that SynthDoG already produces. Paragraph-level groupings are not used in SDG. 
4.   4.Rendering and noise. Pages are rendered at 300 dpi with randomized fonts, font sizes, and background textures (e.g., paper grain). We apply the same noise augmentations as in GL (blur, compression, low-amplitude geometric jitter). 

### B.3 Splits and held-out sets

##### Evaluation pages.

We reserve ∼\sim 10,500 pages across IDL, TabMe++, and PubMed-OCR for evaluation (Section[5.2](https://arxiv.org/html/2601.14490v2#S5.SS2 "5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")). Pages are sampled uniformly at random from the union of these three corpora. All remaining pages from IDL, TabMe++, and PubMed-OCR are used for training or validation.

##### Training and validation splits.

Within each training stage we randomly carve out 2,048 examples from the current training pool as a validation set. Sampling is again stratified by dataset so that every source is represented in validation. These validation examples are held fixed for the duration of the stage and are not reused for training.

##### Early stopping.

We monitor the validation loss once per fixed number of training steps and terminate the current stage when the loss fails to improve for a specified patience window. If the best checkpoint occurs before the end of the stage, we roll back model parameters to that checkpoint before proceeding to the next stage. All random splits are generated with fixed seeds and logged to disk to enable exact reproduction of data partitions.

Appendix C Training
-------------------

### C.1 Input Preprocessing & Setup

During training, we rasterize each PDF page at 72 DPI into a single image and feed it directly to the Qwen2.5-VL NaViT-based vision encoder, preserving the original aspect ratio and using the default maximum number of image tokens without additional cropping, tiling, or high-resolution modes.

##### Backbone configuration.

We fine-tune the public instruction-tuned checkpoints (Qwen2.5-VL-3B-Instruct and Qwen2.5-VL-7B-Instruct) without modifying the tokenizer or vocabulary. All modules of the model are trainable: we do not freeze the vision encoder or language backbone, and we do not introduce adapters or LoRA layers in the GutenOCR models.

##### Context handling.

We train and serve GutenOCR with long-context transcripts, using a curriculum over sequence length described in Section[3.2](https://arxiv.org/html/2601.14490v2#S3.SS2 "3.2 Training recipe ‣ 3 Data & Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). Across stages, we cap the total sequence length (image prompt plus output tokens) between roughly 2k and 16k tokens, always using a single page per example with no dynamic packing across pages. When a target transcript would exceed the stage-specific maximum, we truncate the output and discard the remainder.

At inference time, we enforce the same total-context limits and cap the number of generated tokens at 4,096 on external benchmarks and 16,384 in our internal long-sequence evaluations.

##### Decoding and task routing.

All reported results use deterministic greedy decoding (temperature =0=0, no sampling) with the maximum new-token limits described above. Task routing is purely prompt-based: the user specifies the desired task (reading, detection, localized_reading, or conditional_detection) and output schema (text, text2d, lines, paragraphs, BOX, _etc._) in the prompt, and the same GutenOCR checkpoint is used for all task families. We do not employ any external head-selection logic or multi-model routing.

### C.2 Hyperparameters

Table[13](https://arxiv.org/html/2601.14490v2#A3.T13 "Table 13 ‣ C.2 Hyperparameters ‣ Appendix C Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") summarizes the stage-specific optimization settings used in all experiments. Across stages, we fix the effective batch size to 128 samples (16 per GPU device across 8×\times H100) and use the same optimizer and schedule: AdamW[[33](https://arxiv.org/html/2601.14490v2#bib.bib26 "Decoupled weight decay regularization")] with weight decay 0.01 0.01 and maximum learning rate 1×10−6 1\times 10^{-6}, linearly warmed up over the first 1,000 1{,}000 updates and then linearly decayed to zero. All modules are fully trainable and we use DeepSpeed ZeRO-3 for memory sharding of parameters, optimizer states, and activations. We train in bf16 with gradient checkpointing and clip all gradients to a global norm of 1.0.

Table 13:  Stage-specific optimization settings. Effective batch size is computed as (per-GPU batch) ×\times (gradient accumulation) ×\times 8 GPUs. Dataset mixtures are approximate fractions of pages sampled per stage. SDG = SynthDoG Grounding, GL = Grounded L a T e X, IDL = OCR-IDL, T++ = TabMe++, PMD = PubMed-OCR. 

### C.3 System Prompt

Your task is to read and localize text data from documents and images.

GEOMETRY:

-Coordinates:integer pixels;origin(0,0)top-left;[x1,y1,x2,y2]with x1<x2,y1<y2.

-Clip all boxes to the image bounds;drop boxes with zero/negative area.

-Reading order:read text in natural reading order:top-to-bottom,left-to-right.

-Rotated/angled text:return the axis-aligned bounding box of the minimal enclosing rectangle(no rotated boxes).

TASK TYPES:

-reading:a full-text reading task on the entire image.

-localized_reading:read text within a specified bounding box in the image.

-detection:detect text regions in the image without transcription.

-conditional_detection:detect text regions in the image based on a provided text query.

OUTPUT TYPES:

-TEXT:one plain string;collapse multiple spaces to one;preserve line breaks.Non-grounded output only.

-TEXT2D:one plain string;preserve whitespace as layout cue(spaces+‘\n‘only;no coordinates).Non-grounded output only.

-LINES:JSON array of objects,corresponding to line-by-line OCR:‘{"text":string,"bbox":[x1,y1,x2,y2]}‘.When locally reading,only return the text:‘string’.

-WORDS:JSON array of objects,corresponding to word-by-word OCR:‘{"text":string,"bbox":[x1,y1,x2,y2]}‘.

-PARAGRAPHS:JSON array of objects,corresponding to paragraph-wise OCR:‘{"text":string,"bbox":[x1,y1,x2,y2]}‘.When locally reading,only return the text:‘string‘.

-LATEX:JSON array of objects,corresponding to LaTeX expressions:‘{"text":string,"bbox":[x1,y1,x2,y2]}‘.When locally reading,only return the latex:‘string‘.

-BOX:JSON array of bounding boxes only:‘[[x1,y1,x2,y2],…]‘.For detection and conditional_detection tasks only.

OUTPUT FORMAT

-For non-grounded outputs,return a string:

“‘text

Recognized text goes here.

“‘

“‘text2d

ABSTRACT

Recognition of text in a 2 D layout.

“‘

If the output is empty,return an empty string:

“‘text

“‘

“‘text2d

“‘

-For grounded outputs,return a JSON array of objects when performing reading tasks.

Each object is expected to have two keys:"text"and"bbox".

The"text"key is the what and the"bbox"key is the where.

“‘json

[

{"text":"First line of text","bbox":[100,200,400,250]},

{"text":"Second line of text","bbox":[100,500,400,600]}

]

“‘

“‘json

[

{"text":"\\frac{a}{b}","bbox":[525,558,755,620]}

]

“‘

If the output is empty,return an empty JSON array:

“‘json

[]

“‘

-For detection tasks,return a JSON array of bounding boxes only.

“‘json

[

[100,200,400,250],

[100,500,400,600]

]

“‘

-For localized reading tasks,return the recognized text within the specified bounding box.

“‘text

Recognized text within the bounding box.

“‘

If no text is recognized within the bounding box,return an empty string:

“‘text

“‘

Appendix D Evaluation
---------------------

### D.1 Parsing Structured Outputs

Many baselines and all GutenOCR variants are prompted to emit JSON-structured outputs (e.g., arrays of {"text", "bbox"} pairs). In practice, LLM-generated JSON is frequently imperfect, so we employ a simple repair-and-normalization pipeline before evaluation.

We first pass the raw model output to a tolerant JSON repair library (json_repair), which attempts to recover valid objects even in the presence of unbalanced brackets, missing commas, comments, or extra text around the JSON snippet. If repair fails, the prediction is treated as invalid and assigned the maximal error according to the conventions in Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

For successfully repaired outputs, we normalize key names and shapes: keys whose names contain “text” or “label” (case insensitive) are mapped to a canonical text field; keys containing “box” are mapped to bbox. Lists of four numeric values are interpreted as bounding boxes and wrapped into {"bbox": [x_1,y_1,x_2,y_2]} records when appropriate, and any remaining coordinates are clipped to the image bounds. This normalization allows us to treat structurally similar outputs from different models in a uniform way while still penalizing irreparable or semantically malformed predictions.

### D.2 Metrics

Unless stated otherwise, all text metrics are computed on normalized strings norm⁡(⋅)\operatorname{norm}\!\left(\cdot\right). The normalization operator applies Unicode NFKC, trims leading and trailing whitespace, and collapses internal whitespace runs to a single space. For text2d we preserve line breaks and intra-line spacing before applying norm⁡(⋅)\operatorname{norm}\!\left(\cdot\right) so that layout changes affect the score.

We summarize the formal definitions below for completeness.

#### D.2.1 Text metrics

For a prediction y^\hat{y} and reference y y, let d lev​(⋅,⋅)d_{\text{lev}}(\cdot,\cdot) denote the standard Levenshtein edit distance and |⋅|\left\lvert\cdot\right\rvert the character length. The character error rate (CER) is

CER​(y^,y)=d lev​(norm⁡(y^),norm⁡(y))max⁡(1,max⁡{|norm⁡(y^)|,|norm⁡(y)|}).\mathrm{CER}(\hat{y},y)=\frac{d_{\text{lev}}\bigl(\operatorname{norm}\!\left(\hat{y}\right),\operatorname{norm}\!\left(y\right)\bigr)}{\max\!\bigl(1,\ \max\{\left\lvert\operatorname{norm}\!\left(\hat{y}\right)\right\rvert,\,\left\lvert\operatorname{norm}\!\left(y\right)\right\rvert\}\bigr)}.

Normalizing by the length of the longer string keeps CER∈[0,1]\mathrm{CER}\in[0,1] even when one side is empty or much shorter than the other, which is useful under noisy OCR-derived labels.

For word error rate (WER), we tokenize norm⁡(y)\operatorname{norm}\!\left(y\right) into words using whitespace and let N=|norm⁡(y)|words N=\left\lvert\operatorname{norm}\!\left(y\right)\right\rvert_{\text{words}} be the number of reference words. Let S,D,I S,D,I be the number of substitutions, deletions, and insertions, respectively, when aligning norm⁡(y^)\operatorname{norm}\!\left(\hat{y}\right) to norm⁡(y)\operatorname{norm}\!\left(y\right) at the word level. Then

WER​(y^,y)=S+D+I max⁡(1,N).\mathrm{WER}(\hat{y},y)=\frac{S+D+I}{\max(1,N)}.

#### D.2.2 Detection metrics

Let P={b i}i=1 m P=\{b_{i}\}_{i=1}^{m} be the set of predicted boxes and G={g j}j=1 n G=\{g_{j}\}_{j=1}^{n} the ground-truth boxes, with each box b=[x 1,y 1,x 2,y 2]b=[x_{1},y_{1},x_{2},y_{2}] in image pixel coordinates. We define the intersection-over-union

IoU⁡(b,g)=area⁡(b∩g)area⁡(b∪g).\operatorname{IoU}(b,g)=\frac{\operatorname{area}(b\cap g)}{\operatorname{area}(b\cup g)}.

For a threshold τ\tau (we use τ=0.5\tau=0.5 throughout), we construct a one-to-one matching M τ⊆P×G M_{\tau}\subseteq P\times G using only pairs with IoU≥τ\operatorname{IoU}\geq\tau (Hungarian matching with IoU as affinity). We then define

TP τ=|M τ|,FP τ=m−TP τ,FN τ=n−TP τ.\mathrm{TP}_{\tau}=\lvert M_{\tau}\rvert,\quad\mathrm{FP}_{\tau}=m-\mathrm{TP}_{\tau},\quad\mathrm{FN}_{\tau}=n-\mathrm{TP}_{\tau}.

Precision, recall, and F1 at threshold τ\tau are

Prec τ=TP τ max⁡(1,TP τ+FP τ),Rec τ={1,|G|=0,TP τ/|G|,|G|>0,\text{Prec}_{\tau}=\frac{\mathrm{TP}_{\tau}}{\max(1,\mathrm{TP}_{\tau}+\mathrm{FP}_{\tau})},\quad\text{Rec}_{\tau}=\begin{cases}1,&|G|=0,\\[2.5pt] \mathrm{TP}_{\tau}/|G|,&|G|>0,\end{cases}

F1 τ=2​Prec τ​Rec τ max⁡(1,Prec τ+Rec τ).\text{F1}_{\tau}=\frac{2\,\text{Prec}_{\tau}\,\text{Rec}_{\tau}}{\max(1,\text{Prec}_{\tau}+\text{Rec}_{\tau})}.

In the main text we report F1​@​0.5≡F1 τ=0.5\mathrm{F1@0.5}\equiv\text{F1}_{\tau=0.5} and Recall​@​0.5≡Rec τ=0.5\mathrm{Recall@0.5}\equiv\text{Rec}_{\tau=0.5}.

#### D.2.3 End-to-end metrics (detection + recognition)

For structured reading tasks that produce box–text pairs P={(b i,t^i)}P=\{(b_{i},\hat{t}_{i})\} and G={(g j,t j)}G=\{(g_{j},t_{j})\} we use two end-to-end metrics that reuse the detection matching M 0.5 M_{0.5} from Section[D.2.2](https://arxiv.org/html/2601.14490v2#A4.SS2.SSS2 "D.2.2 Detection metrics ‣ D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

##### mCER@0.5 (recognition given correct localization).

Let M 0.5 M_{0.5} be the one-to-one matching between predicted and ground-truth boxes at IoU≥0.5\geq 0.5. For each (i,j)∈M 0.5(i,j)\in M_{0.5} we compute a per-span CER

cer i,j=d lev​(norm⁡(t^i),norm⁡(t j))max⁡(1,max⁡{|norm⁡(t^i)|,|norm⁡(t j)|}).\mathrm{cer}_{i,j}=\frac{d_{\text{lev}}\bigl(\operatorname{norm}\!\left(\hat{t}_{i}\right),\operatorname{norm}\!\left(t_{j}\right)\bigr)}{\max\!\bigl(1,\ \max\{\left\lvert\operatorname{norm}\!\left(\hat{t}_{i}\right)\right\rvert,\,\left\lvert\operatorname{norm}\!\left(t_{j}\right)\right\rvert\}\bigr)}.

mCER@0.5 is the mean of cer i,j\mathrm{cer}_{i,j} over (i,j)∈M 0.5(i,j)\in M_{0.5}, with edge cases handled as described below. Because unmatched ground-truth boxes do not contribute directly to this average, mCER@0.5 isolates recognition quality conditioned on successful localization; coverage is accounted for by the detection recall.

##### CER e2e\text{CER}_{\text{e2e}} (page-level fidelity).

To assess the joint effect of localization, reading order, insertions, and deletions, we form page-level strings from P P and G G as follows. We sort boxes in a deterministic reading order (by the y 1 y_{1} coordinate of their top edge, then by x 1 x_{1} left-to-right), concatenate the corresponding texts with line breaks and layout-sensitive whitespace (as in the text2d construction), and finally apply norm⁡(⋅)\operatorname{norm}\!\left(\cdot\right) to both page strings. We then compute CER between these two concatenated strings. CER e2e\text{CER}_{\text{e2e}} is therefore sensitive to missing or spurious lines, scrambled ordering, and layout-preserving whitespace errors in addition to pure recognition mistakes.

#### D.2.4 Edge cases and invalid predictions

We adopt the following conventions to keep metrics well defined:

*   •Empty text. If both normalized strings are empty, we set CER=0\mathrm{CER}=0 and WER=0\mathrm{WER}=0. If exactly one side is empty, we set CER=1\mathrm{CER}=1 and WER=1\mathrm{WER}=1. 
*   •

Detection with no boxes.

    *   –P=∅P=\varnothing and G=∅G=\varnothing: (Prec,Rec,F1)=(1,1,1)(\text{Prec},\text{Rec},\text{F1})=(1,1,1). 
    *   –G=∅G=\varnothing and P≠∅P\neq\varnothing: Rec=1\text{Rec}=1, Prec=0\text{Prec}=0, so F1=0\text{F1}=0. 
    *   –P=∅P=\varnothing and G≠∅G\neq\varnothing: Rec=0\text{Rec}=0 and F1=0\text{F1}=0. 

*   •mCER@0.5 with no matches. If |M 0.5|>0|M_{0.5}|>0, mCER@0.5 is the average over matched pairs. If P=∅P=\varnothing and G=∅G=\varnothing, we set mCER​@​0.5=0\mathrm{mCER@0.5}=0. In all other cases with |M 0.5|=0|M_{0.5}|=0 (e.g., detector fires but never overlaps ground truth, or misses all ground-truth boxes) we set mCER​@​0.5=1\mathrm{mCER@0.5}=1. 
*   •Invalid structured predictions. If a model output cannot be repaired into valid JSON or yields no usable boxes/text after normalization (Appendix[D.1](https://arxiv.org/html/2601.14490v2#A4.SS1 "D.1 Parsing Structured Outputs ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), we treat it as a maximal-error prediction: CER=1\mathrm{CER}=1, WER=1\mathrm{WER}=1. For structured tasks we additionally set mCER​@​0.5=1\mathrm{mCER@0.5}=1 and CER e2e=1\text{CER}_{\text{e2e}}=1, and assign F1​@​0.5=0\mathrm{F1@0.5}=0 and Recall​@​0.5=0\mathrm{Recall@0.5}=0 for the associated detection metrics. 

##### Composite grounded OCR score.

For the composite scores reported in Section[5.2](https://arxiv.org/html/2601.14490v2#S5.SS2 "5.2 In-Domain ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), we map each reading error ϵ∈[0,1]\epsilon\in[0,1] (CER, WER, mCER@0.5, or CER e2e\text{CER}_{\text{e2e}}) to a per-task score 1−ϵ 1-\epsilon, and average these scores with the corresponding detection and conditional-detection F1@0.5 values over the task families in Table[4](https://arxiv.org/html/2601.14490v2#S4.T4 "Table 4 ‣ 4.1 Metrics ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"). The resulting composite lies in [0,1][0,1] and weights reading and detection tasks equally.

Appendix E Additional Benchmark Details
---------------------------------------

### E.1 Fox Benchmark Details

This section supplements the main Fox results in Section[5.3](https://arxiv.org/html/2601.14490v2#S5.SS3 "5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") and Table[7](https://arxiv.org/html/2601.14490v2#S5.T7 "Table 7 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") with task configuration, prompting details, and a more detailed discussion of the Page F1 vs. Page CER trade-off and of the region, line, and color-guided subtasks.

##### Tasks and filtering.

Fox[[29](https://arxiv.org/html/2601.14490v2#bib.bib5 "Focus Anywhere for Fine-grained Multi-page Document Understanding")] defines a collection of multi-page document tasks that mix OCR, retrieval, and visual reasoning. We restrict our evaluation to the four English OCR-style subtasks that align with GutenOCR’s training objectives: (i) page OCR, (ii) region-level OCR, (iii) line-level OCR, and (iv) color-guided OCR. We follow the official Fox splits and evaluation scripts, but filter pages to those whose language metadata is purely English.

##### Output canonicalization.

For the page OCR subtask, we score predictions as plain text. In practice, some models emit lightweight structure or markup (e.g., JSON wrappers, Markdown, or HTML) rather than a raw transcript. To make evaluation robust to these surface forms, we apply a uniform post-processing step that attempts to detect and render such outputs into a single text string prior to scoring (Markdown is rendered via markdown2, HTML is stripped via BeautifulSoup, and JSON outputs are parsed and linearized into a text representation). This canonicalization is applied identically to all models, but it may mildly benefit systems that produce well-formed structured/marked-up outputs by allowing their textual content to be recovered instead of being penalized for formatting alone.

##### Prompting and decoding.

All models, including GutenOCR and Qwen-based baselines, are evaluated under a unified prompting scheme. For each Fox subtask, we use the official benchmark prompts and output-format instructions as provided by the evaluation scripts. For the region- and line-level OCR tasks (which include an explicit pointer region), the only model-specific adaptation we apply is a deterministic conversion of the pointer box into the coordinate convention expected by the model (e.g., absolute pixel coordinates vs. normalized coordinates). Beyond this box-format normalization, prompts are otherwise unchanged across models.

For baselines, we apply a minimal OCR-focused system prompt (Listing[E.1](https://arxiv.org/html/2601.14490v2#A5.SS1.SSS0.Px3 "Prompting and decoding. ‣ E.1 Fox Benchmark Details ‣ Appendix E Additional Benchmark Details ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")) to encourage strict format compliance (e.g., emitting raw JSON when requested). For GutenOCR, we preserve the exact system prompt used during training (see Appendix[C.3](https://arxiv.org/html/2601.14490v2#A3.SS3 "C.3 System Prompt ‣ Appendix C Training ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")), without modification.

All results are produced with deterministic greedy decoding (temperature =0=0, no sampling) and a fixed maximum new-token budget.

You are an OCR assistant.Read and transcribe text from the provided document image.

Follow the user’s instructions exactly.

Do not add explanations or extra text beyond the requested output.

##### Page metrics: Page F1 vs. Page CER.

Fox reports an order-agnostic _Page F1_ metric that measures the overlap between predicted and reference tokens after text normalization and an order-sensitive edit-distance metric. In our tables, we retain Page F1 and replace the latter with our normalized character error rate (CER; Section[4.1](https://arxiv.org/html/2601.14490v2#S4.SS1 "4.1 Metrics ‣ 4 Evaluation Setup ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")). Intuitively:

*   •Page F1 is forgiving of reading order and extra whitespace. It treats the page as a bag (or multiset) of tokens and measures how many reference tokens appear somewhere in the prediction, and vice versa. 
*   •Page CER is stricter: predictions are compared to the canonical Fox linearization as a single string, so reordering blocks, inserting extra text, or missing spans all increase the error. 

GutenOCR is trained to emit layout-sensitive text2d and structured line/paragraph JSON outputs, not a single canonical page-to-Markdown format. On Fox pages, it therefore tends to obey 2D layout cues (columns, tables, headings, whitespace) rather than the specific reading order chosen by the benchmark. As a result, GutenOCR-3B and GutenOCR-7B achieve very high Page F1 (close to or above their Qwen2.5-VL backbones) while exhibiting substantially worse Page CER: they read essentially the right content, but prefer to do so in a layout-driven order that diverges from Fox’s reference markup.

In contrast, OCR-specialized baselines like Nanonets-OCR2-3B and olmOCR 2 are explicitly optimized for page-to-Markdown fidelity and thus better match Fox’s canonical order, yielding lower Page CER at similar or slightly lower Page F1. We view this discrepancy as reflecting a difference in target behavior rather than a pure weakness: GutenOCR prioritizes layout-preserving, grounded front-end outputs, whereas Fox’s page metric rewards adherence to a particular markup convention.

##### Region- and line-level OCR.

Region and line subtasks probe the ability to “focus anywhere” on the document. Fox provides, for each query, either a region pointer (a box highlighted on the page) or a line pointer, together with a target transcript. We evaluate all models by cropping the indicated region/line from the page, passing the full page plus pointer to the model, and computing CER between the normalized prediction and reference text.

GutenOCR is closest to these tasks in spirit: it is explicitly trained for region-aware reading and localized reading given a box. As reported in Table[7](https://arxiv.org/html/2601.14490v2#S5.T7 "Table 7 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), this specialization yields large gains over the Qwen2.5-VL backbones on both region and line tasks, and GutenOCR-3B attains the best region-level CER among all evaluated models, slightly outperforming the dedicated Fox model itself. The line task is somewhat extrapolative for GutenOCR (we do not train on explicit line-pointer prompts), but we still see substantial improvements, which we attribute to transfer from region-level detection and localized reading: once the model can reliably find and read arbitrary subregions, line pointers become a natural special case.

##### Color-guided OCR and catastrophic forgetting.

The color-guided task asks the model to read only text in a colored box (red/green/blue) while ignoring all other text. Fox and several OCR-specialized baselines perform strongly here; Qwen2.5-VL-7B also demonstrates a reasonable zero-shot ability to interpret color-coded pointers, likely inherited from generic vision-and-grounding pretraining.

GutenOCR, by contrast, performs poorly on this subtask (high CER for both 3B and 7B). We do not include any color-guided supervision in our training mixture, and the OCR-centric fine-tuning appears to overwrite the heuristics the base VLMs had learned for color-based selection. Qualitatively, we frequently observe GutenOCR interpreting prompts literally (e.g., trying to read the words “red box” from the page) or returning structured box coordinates instead of the requested text. This is a classic example of narrow catastrophic forgetting: the documentation-focused curriculum strengthens grounded OCR in the regime we care about (full-page, region, and localized reading) while eroding an orthogonal emergent behavior (color-conditioned region selection) that was never exercised during fine-tuning.

##### Qualitative examples.

Figure[4](https://arxiv.org/html/2601.14490v2#S5.F4 "Figure 4 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") illustrates typical Fox behaviors for Qwen2.5-VL-3B vs. GutenOCR-3B:

*   •Region/line success. In panels (a) and (b), Qwen2.5-VL-3B either misses or badly misreads the targeted snippet, while GutenOCR returns the correct localized text with near-zero CER, showing transfer of its in-domain grounding abilities. 
*   •Color failure. Panel (c) shows a case where Qwen2.5-VL-3B perfectly follows the color box, whereas GutenOCR essentially ignores the color cue. 
*   •Content vs. structure. Panel (d) provides a concrete Page F1 vs. Page CER example: GutenOCR captures almost all of the reference tokens (high F1) but streams them in a layout-driven order that diverges from the Fox linearization, leading to a higher CER than the backbone despite better underlying reading. 

These examples match the quantitative pattern in Table[7](https://arxiv.org/html/2601.14490v2#S5.T7 "Table 7 ‣ 5.3 Fox ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"): GutenOCR behaves like a grounded OCR front-end—strong on region and line reading, layout-sensitive in its page outputs, and relatively agnostic to color cues—rather than like a page-to-Markdown system tuned for a single canonical reading order.

### E.2 OmniDocBench v1.5

OmniDocBench v1.5[[39](https://arxiv.org/html/2601.14490v2#bib.bib25 "OmniDocBench: benchmarking diverse pdf document parsing with comprehensive annotations")] is a multi-domain document benchmark built from PDF pages with dense annotations for layout regions, text spans, formulas, and tables. The corpus covers nine page types—books, slides, financial reports, textbooks, exam papers, magazines, academic papers, handwritten notes, and newspapers—with a v1.0→\rightarrow 1.5 revision that expands coverage and refines markup conventions.2 2 2 See the v1.0→\rightarrow 1.5 changelog in the OmniDocBench supplement. The official tasks focus on end-to-end markup generation (e.g., HTML/Markdown) and report a combination of edit-distance and structure-aware metrics for text, formulas, and tables.

Our production setting targets grounded text+box outputs rather than canonical markup, so we use OmniDocBench as a testbed for three task-specific behaviors: _text recognition_, _formula recognition_, and _text detection_. Throughout, we restrict to pages whose language tag is purely English.

##### Text recognition subset.

For text recognition we use the OmniDocBench OCR subset, which provides cropped text spans together with attributes such as language, background type, and rotation. Each span is paired with a reference transcript, and evaluation is based on component-level edit distance. We follow the official setup and compute character error rate (CER) on either (i) full-page concatenations (page-level OCR) or (ii) individual cropped spans (component-level OCR), grouping results by attributes such as background (white, single-color, multi-color) and page type. In all cases we apply the same string normalization norm⁡(⋅)\operatorname{norm}\!\left(\cdot\right) as in Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") before computing CER.

##### Formula recognition subset.

OmniDocBench includes a dedicated formula subset with L a T e X annotations for rendered equations. The official benchmark evaluates formulas using the Character Detection Matching (CDM) metric[[52](https://arxiv.org/html/2601.14490v2#bib.bib58 "Image over text: transforming formula recognition evaluation with character detection matching")], which compares rendered strings at the symbol level, together with normalized edit distance. We adopt this setup for the English subset: for each cropped formula we render both the reference and predicted L a T e X and compute (i) CER between normalized strings, and (ii) CDM as a render-aware similarity score (higher is better). Results in the main text (Table[11](https://arxiv.org/html/2601.14490v2#S5.T11 "Table 11 ‣ 5.4.3 Formula Recognition ‣ 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")) break these metrics down by page type to surface domain-specific trends.

##### Layout and text-detection subset.

For layout, OmniDocBench provides text spans defined at roughly line level, together with higher-level layout regions such as tables and formula blocks. Crucially for our purposes, the text spans form a _partial_ annotation of visible text:

*   •Many table cells are represented only through a table object rather than individual text spans. 
*   •Certain formulas and labels are marked with special tags (e.g., Equation Ignore) to exclude them from text-based evaluation. 
*   •Decorative or low-salience text may be omitted entirely. 

GutenOCR, by contrast, is trained under a “detect all readable text” ontology: it aims to place line-level boxes on any legible text, including table cells, equation-like expressions, and decorative labels. As a result, a one-to-one mapping between OmniDocBench spans and our notion of “text line” does not exist.

##### Recall-only detection protocol.

Because OmniDocBench text spans cover only a subset of the text that GutenOCR legitimately detects, we cannot reliably treat non-overlapping predictions as false positives. Any predicted box with no matching annotated span might be: (i) a true positive under our ontology (e.g., content inside a table cell), or (ii) a genuine hallucination; the benchmark does not distinguish between these cases. This makes precision and F1 ill-defined for our setting.

To avoid over-interpreting partial labels, we treat OmniDocBench text spans as a _trusted but incomplete_ ground-truth set and evaluate only recall at IoU≥0.5\geq 0.5:

> When OmniDocBench says “there is text here”, how often does our detector cover it?

Concretely, we compute R@0.5 by matching predicted and ground-truth boxes using IoU≥0.5\geq 0.5 (as in Appendix[D.2](https://arxiv.org/html/2601.14490v2#A4.SS2 "D.2 Metrics ‣ Appendix D Evaluation ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents")) and report the fraction of annotated spans that receive a match. We do not report precision or F1 on OmniDocBench text detection.

Qualitatively, this protocol corresponds to counting red (annotated) boxes that are covered by blue (predicted) boxes in examples such as Figure[5](https://arxiv.org/html/2601.14490v2#S5.F5 "Figure 5 ‣ 5.4.1 Text Recognition ‣ 5.4 OmniDocBench v1.5 ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents"), while ignoring extra blue boxes on unannotated but readable text (table cells, decorative labels, etc.). Higher recall under this metric therefore indicates better coverage of the annotated subset, without making claims about behavior on the unannotated portion of the page.

Appendix F Models
-----------------

We group baselines into two categories: (i) general-purpose Qwen-based VLMs used in a prompting-only setting, and (ii) OCR-specialized or layout-focused models built on Qwen or other backbones. A high-level overview of all models, including parameter counts, backbones, and whether their public interfaces expose coordinates, is given in Table[5](https://arxiv.org/html/2601.14490v2#S5.T5 "Table 5 ‣ 5.1 Models ‣ 5 Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents").

##### Qwen2.5-VL

Qwen2.5-VL[[4](https://arxiv.org/html/2601.14490v2#bib.bib16 "Qwen2.5-vl technical report")] is a general-purpose vision–language model trained on a mixture of image–text, document-understanding, OCR, and spatial-grounding tasks, including referring expressions and box/point localization. In its native interface, spatial outputs are expressed as absolute pixel coordinates in the input image frame (e.g., bounding boxes ([x 1,y 1,x 2,y 2])([x_{1},y_{1},x_{2},y_{2}])), which matches our detection and localized-reading conventions. We use the off-the-shelf instruct models (3B/7B) as prompting-only baselines for our reading, detection, conditional-detection, and localized-reading tasks, specifying the desired output schema (plain text, layout-sensitive text, or JSON with boxes) in the prompt.

##### Qwen3-VL

Qwen3-VL-8B[[3](https://arxiv.org/html/2601.14490v2#bib.bib17 "Qwen3-vl technical report")] is an 8B-parameter vision–language model trained on large-scale OCR, document parsing, long-document VQA, and 2D/3D grounding and counting data, in addition to generic image–text and VQA corpora. Spatial supervision is provided through both bounding-box and point annotations, represented in a normalized coordinate system scaled to [0,1000][0,1000] along each image axis, which we map to pixel coordinates for evaluation. We use the off-the-shelf Qwen3-VL-8B instruct model as another prompting-only baseline, again prompting for the desired output schema (plain text, layout-aware text, or JSON with boxes).

##### Nanonets OCR2-3B

Nanonets-OCR2-3B[[35](https://arxiv.org/html/2601.14490v2#bib.bib20 "Nanonets-ocr2: a model for transforming documents into structured markdown with intelligent content recognition and semantic tagging")] is a 3B-parameter OCR-specialized vision–language model obtained by fine-tuning Qwen2.5-VL-3B-Instruct on a >3>\!3 M-page corpus of synthetic and manually annotated documents for image-to-Markdown OCR and document-focused visual question answering. The model takes a document page as input and produces a single structured Markdown string with semantic tags for equations, tables, images, signatures, watermarks, checkboxes, page numbers, and flowcharts, but does not expose bounding-box coordinates or region-level grounding outputs. In our evaluation, we primarily use Nanonets-OCR2-3B as a strong baseline for page-level reading and tag-level content extraction, and additionally probe its performance on our coordinate-based detection and grounding tasks to assess how much of the underlying Qwen2.5-VL-3B spatial reasoning ability is retained after OCR specialization.

##### olmOCR 2

olmOCR 2[[42](https://arxiv.org/html/2601.14490v2#bib.bib18 "OlmOCR 2: unit test rewards for document ocr")] is an OCR-specialized 7B vision–language model obtained by further fine-tuning Qwen2.5-VL-7B-Instruct with supervised training and reinforcement learning with verifiable rewards (RLVR) on synthetic HTML-rendered pages, using unit tests that score only the correctness of a linearized textual transcript (reading order, tables, math rendering, etc.). The public system takes a rasterized PDF page as input and emits YAML whose body is plain Markdown text, without explicit bounding boxes or coordinates. We therefore regard olmOCR 2 as a strong baseline for page-level reading and use our evaluation to quantify how much of the base model’s detection and referring ability is lost under OCR-focused specialization.

##### Infinity-Parser-7B

Infinity-Parser-7B[[51](https://arxiv.org/html/2601.14490v2#bib.bib19 "Infinity parser: layout aware reinforcement learning for scanned document parsing")] is a layout-aware document-parsing model obtained by fine-tuning Qwen2.5-VL-7B on the Infinity-Doc-55K corpus of scanned pages paired with structured Markdown and table/formula annotations, using a reinforcement-learning objective that combines normalized edit distance, paragraph-count accuracy, and reading-order preservation. The public model takes page images as input and produces Markdown (with region segments wrapped in <ele> tags) and HTML tables, but does not emit bounding boxes or coordinates. We treat Infinity-Parser-7B as a strong baseline for page-level reading and layout-sensitive parsing, and additionally evaluate it on our grounding tasks to measure how much of the Qwen2.5-VL-7B base model’s detection and referring ability remains after layout-focused RL tuning.

##### Chandra OCR

Chandra[[41](https://arxiv.org/html/2601.14490v2#bib.bib21 "Introducing our newest model: chandra")] is a layout-preserving OCR system built on top of the Qwen3-VL vision–language model, trained to convert full document pages into structured HTML/Markdown/JSON while handling complex layouts, handwriting, tables, forms, math, and images. The model outputs HTML comprising block-level <div> elements annotated with semantic labels (e.g., text, image, figure, table) and bounding boxes in a normalized 1024×1024 1024\times 1024 coordinate system via data-bbox attributes, which the library rescales to pixel coordinates for downstream processing. We primarily use Chandra as a baseline for page-level reading and block-level detection in our taxonomy, and additionally test it on our finer-grained line-level and conditional grounding tasks, which go beyond the capabilities explicitly targeted by its training.

##### DeepSeek-OCR

DeepSeek-OCR[[59](https://arxiv.org/html/2601.14490v2#bib.bib22 "DeepSeek-ocr: contexts optical compression")] is a 3B-parameter vision–language OCR model composed of a custom high-resolution vision encoder (DeepEncoder) and a DeepSeek-3B-MoE decoder, trained on a large mixture of document OCR, synthetic “OCR 2.0” (charts, chemical formulas, geometry), natural-scene OCR, general vision (caption/detection/grounding), and text-only data. Document pages are supervised with both coarse text-only labels and fine layout annotations in which each paragraph is preceded by its region label and bounding-box coordinates normalized to 1,000 bins, enabling the model to emit layout-aware text paired with coordinates as well as plain transcripts. We use DeepSeek-OCR as a baseline for page-level reading and layout-sensitive parsing, and further evaluate it on our detection and conditional grounding tasks to probe its referring and object-localization capabilities.

##### PaddleOCR-VL

PaddleOCR-VL-0.9B[[9](https://arxiv.org/html/2601.14490v2#bib.bib23 "PaddleOCR-vl: boosting multilingual document parsing via a 0.9b ultra-compact vision-language model")] is a compact, document-specialized VLM trained for element-level recognition (OCR, tables, formulas, charts) but not for layout detection or box prediction. In the full PaddleOCR system, a separate layout model (PP-DocLayoutV2) first predicts element types, boxes, and reading order; cropped regions are then fed to PaddleOCR-VL-0.9B, which is trained—via a 29M pretraining set plus 2.7M instruction samples—to output structured text such as Markdown/JSON, OTSL tables, and L a T e X formulas. In our evaluation we explicitly use only the PaddleOCR-VL-0.9B VLM as another OCR/document-parsing baseline, and do not rely on their separate layout-analysis stage.

Appendix G Additional Results
-----------------------------

### G.1 Detailed In-Domain Evaluation

#### G.1.1 Reading

##### Structured, line-based reading.

Table 14:  Structured, line-based full-page reading on OCR-IDL, TabMe++, and PubMed-OCR. CER e2e{}_{\text{e2e}} is the page-level character error rate on the concatenated transcript; mCER is computed only on lines whose boxes are correctly matched. All values are errors (lower is better, ↓\downarrow). Within each column, bold numbers indicate the best value across all models; underlined numbers are best within each backbone cohort (3B vs. 7B). Entries that are both bold and underlined are best both overall and within their cohort. 

GutenOCR converts both Qwen2.5-VL backbones from “good reader, bad paginator” into stable structured readers. On the 3B backbone, Stage 1 roughly halves average CER e2e{}_{\text{e2e}} and cuts mCER by about 80% relative to Qwen2.5-VL-3B, with Stages 2 and 3a mostly refining per-line recognition (mCER) at similar page-level error. On the 7B backbone, Stage 1 achieves the lowest overall CER e2e{}_{\text{e2e}} and Stage 3a the lowest mCER, eliminating the large gap between strong per-line accuracy and poor page assembly seen in the raw Qwen2.5-VL-7B model. Stage 3b over-specializes to PubMed-OCR, improving that domain at a modest cost to the business datasets.

Table 15:  Full-page reading with linearized text output. We report character error rate (CER) and word error rate (WER), lower is better (↓\downarrow). Bold numbers indicate the best value in each column across all models; underlined numbers are best within each backbone cohort. 

Table[15](https://arxiv.org/html/2601.14490v2#A7.T15 "Table 15 ‣ Structured, line-based reading. ‣ G.1.1 Reading ‣ G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") shows plain-text OCR where each page is reduced to a single transcript. Scaling from 3B to 7B already helps substantially, but GutenOCR fine-tuning dominates: all GutenOCR variants reduce CER and WER versus their backbones. Stage 1 gives the lowest average CER for both sizes, while Stage 3a trades a small amount of CER for noticeably better WER, especially on PubMed-OCR. Stage 3b again behaves as a PubMed-OCR specialist. Overall, GutenOCR-7B Stage 3a is the strongest linear-text reader, with GutenOCR-3B Stage 1/3a as competitive, cheaper options.

##### Layout-sensitive text2d.

Table 16:  Full-page reading with layout-preserving text2d output. We report CER and WER, lower is better (↓\downarrow). Bold numbers denote the best value in each column; underlined numbers are best within each backbone cohort. 

Table[16](https://arxiv.org/html/2601.14490v2#A7.T16 "Table 16 ‣ Layout-sensitive text2d. ‣ G.1.1 Reading ‣ G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") evaluates layout-preserving text2d, which is stricter than linear text because whitespace carries layout information. Both GutenOCR backbones roughly halve CER and WER relative to their Qwen baselines. Stage 1 gives the lowest CER on average, while Stage 3a improves WER by better handling of spaces and line breaks, again especially on PubMed-OCR. After fine-tuning, differences between GutenOCR-3B and GutenOCR-7B in this setting are small compared to the gains over the original VLMs.

#### G.1.2 Localized Reading

Table 17:  Localized reading from ground-truth regions. We report CER and WER, lower is better (↓\downarrow). Bold entries are best overall per column; underlined entries are best within each backbone cohort. 

##### Localized reading from ground-truth regions.

Table[17](https://arxiv.org/html/2601.14490v2#A7.T17 "Table 17 ‣ G.1.2 Localized Reading ‣ G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") evaluates recognition given ground-truth boxes. GutenOCR dramatically improves both backbones: average CER drops from ≈\approx 0.7/0.53 to the 0.11–0.20 range and WER from ≈\approx 0.8/0.67 to 0.20–0.32. Unlike full-page reading, GutenOCR-3B Stage 3a achieves the best overall CER and WER, with GutenOCR-7B stages close behind. Stage 3b again tilts toward PubMed-OCR, improving that domain while slightly degrading business-document performance.

#### G.1.3 Detection

Table 18:  Full-page line detection. We report F1 and recall (R), higher is better (↑\uparrow). Bold numbers indicate the best value across all models; underlined numbers are best within each backbone cohort. 

##### Full-page line detection.

Table[18](https://arxiv.org/html/2601.14490v2#A7.T18 "Table 18 ‣ G.1.3 Detection ‣ G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") shows that the raw Qwen2.5-VL models are very weak detectors (F1 ≈\approx 0.1). GutenOCR raises both F1 and recall to around 0.75–0.82 across datasets for both 3B and 7B, turning the backbones into strong line detectors with only small size-dependent differences. Stage 1 offers the best general-purpose detector, Stage 3a slightly favors TabMe++, and Stage 3b leans toward PubMed-OCR, but all GutenOCR stages are a large step up from the prompting-only baselines.

#### G.1.4 Conditional Detection

Table 19:  Conditional line detection given a query string. We report F1 and recall (R), higher is better (↑\uparrow). Bold entries are best overall per column; underlined entries are best within backbone. 

##### Phrase-conditioned detection.

Table[19](https://arxiv.org/html/2601.14490v2#A7.T19 "Table 19 ‣ G.1.4 Conditional Detection ‣ G.1 Detailed In-Domain Evaluation ‣ Appendix G Additional Results ‣ GutenOCR: A Grounded Vision–Language Front-End for Documents") summarizes phrase-conditioned detection (“where is string q q on this page?”). While Qwen2.5-VL-7B is noticeably better than 3B out of the box, both backbones are far from usable. GutenOCR pushes F1 and recall into the 0.85–0.90 range across datasets, with Stage 3a giving the best average performance and Stage 3b again specializing toward PubMed-OCR. In this setting the 7B model keeps a small but consistent edge over 3B, reflecting its stronger underlying recognition once detection has been trained.

