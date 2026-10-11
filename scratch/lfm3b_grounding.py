"""LFM2.5-VL-3B grounding exactly as Liquid documents it
(docs.liquid.ai/lfm/key-concepts/vision-capabilities#object-detection-and-grounding): the
system prompt, the image before the request, a plain-language request, free (unconstrained)
JSON, and the documented sampling. Each page asks for its schema's values by description;
the title page also asks for each author's exact name. Every box is checked against the PDF
text layer. Run `task vllm` first to forward the server."""

import json
from pathlib import Path

import cv2
import pypdfium2 as pdfium
from openai import OpenAI

from lfm3b_vl import GROUNDING_SYSTEM_PROMPT
from qwen_vl import TEST_CASES, VLLM_URL, pdf_text, render_page, to_data_url, to_pixels

MODEL = "lfm-vl"
OUTPUT_DIR = Path(__file__).parent / "out" / "lfm-3b-documented"
RUNS = 2
# Plain-language requests, in the style of the docs' "Provide bounding boxes for the two cats
# and the two remote controls."
REQUESTS = {
    "title_page": "Provide bounding boxes for the document title and each author's name, "
    "without their affiliation.",
    "citations_chicago": "Provide bounding boxes for the title of each cited work in the "
    "reference list, without its authors, year, venue or URL.",
    "citations_quoted": "Provide bounding boxes for the title of each cited work in the "
    "reference list, without its authors, year, venue or URL.",
    "table_cells": "Provide bounding boxes for the 2023 average amount of time deposits, the "
    "2022 average rate on total deposits, and the 2024 average rate on savings and demand "
    "deposits.",
}
AUTHORS = ["UDAYAN DAS", "AUBREY LAWSON", "CHRIS MAYFIELD", "NARGES NOROUZI"]


def ground(client: OpenAI, image_url: str, request: str) -> list[dict] | str:
    """The documented request; the parsed array, or the raw text when it isn't JSON."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": GROUNDING_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": request},
                ],
            },
        ],
        # The docs' sampling settings; max_new_tokens=256 there is for four boxes
        temperature=0.2,
        max_tokens=4096,
        extra_body={"top_k": 50, "repetition_penalty": 1.0},
    )
    content = response.choices[0].message.content or ""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return content


def show(page, textpage, image, detections, overlay_path: Path) -> None:
    if isinstance(detections, str):
        print(f"  not JSON: {detections[:200]!r}")
        return
    overlay = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    height, width = image.shape[:2]
    for detection in detections:
        box = detection.get("bbox_2d")
        if not isinstance(box, list) or len(box) != 4:
            print(f"  malformed: {detection}")
            continue
        print(
            f"  {detection.get('label')!r:<45} pdf: {pdf_text(page, textpage, box)!r}"
        )
        x1, y1, x2, y2 = to_pixels(box, width, height)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 128, 255), 2)
    overlay_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(overlay_path), overlay)


def main():
    client = OpenAI(base_url=VLLM_URL, api_key="unused")
    print(f"Model: {client.models.list().data[0].root}")
    for name, pdf_path, page_index, _ in TEST_CASES:
        with pdfium.PdfDocument(pdf_path) as pdf:
            page = pdf[page_index]
            textpage = page.get_textpage()
            image = render_page(page)
            image_url = to_data_url(image)
            for run in range(1, RUNS + 1):
                print(f"\n## {name}, run {run}: {REQUESTS[name]}")
                show(
                    page,
                    textpage,
                    image,
                    ground(client, image_url, REQUESTS[name]),
                    OUTPUT_DIR / f"{name}_{run}.png",
                )
            if name == "title_page":
                for author in AUTHORS:
                    request = f'Provide bounding boxes for the text "{author}".'
                    print(f"\n## {name}: {request}")
                    show(
                        page,
                        textpage,
                        image,
                        ground(client, image_url, request),
                        OUTPUT_DIR / f"{name}_{author.split()[0].lower()}.png",
                    )


if __name__ == "__main__":
    main()
