"""The qwen_vl.py tests on LFM2.5-VL-3B. Given the grounding system prompt from Liquid's
LFM2.5-VL-3B WebGPU demo, it reports Qwen-style bbox_2d integers in [0, 1000]. Each page runs
one grounded extraction call, then the cookbook-style extraction with each value located in its
own call. Run `task vllm` first to forward the server."""

from pathlib import Path

import pypdfium2 as pdfium
from openai import OpenAI
from pydantic import BaseModel, RootModel, ValidationError, conlist

from lfm_vl import ask, describe, extract, ground_values
from qwen_vl import (
    TEST_CASES,
    VLLM_URL,
    Box,
    grounded,
    render_page,
    report,
    to_data_url,
)

OUTPUT_DIR = Path(__file__).parent / "out" / "lfm-3b"
# From the demo (huggingface.co/spaces/LiquidAI/LFM2.5-VL-3B-WebGPU, src/main.js)
GROUNDING_SYSTEM_PROMPT = """When asked for bounding boxes for objects, return a valid JSON array.
Each array item must be an object with:
- image_id: the 0-based index of the image
- bbox_2d: [xmin, ymin, xmax, ymax] normalized integer coordinates in [0, 1000]
- label: a concise label you choose for the predicted object or region

Return one item per visible matching object or region. Return [] if none are visible."""
# Keeps a detection that never stops from running to the token limit
MAX_DETECTIONS = 10


class Detection(BaseModel):
    image_id: int
    bbox_2d: Box
    label: str


def extract_grounded(
    client: OpenAI, image_url: str, schema: type[BaseModel]
) -> BaseModel:
    return ask(
        client,
        image_url,
        "Extract the following from the document, copying text exactly as printed, and "
        "provide a bounding box for each value. Present as a JSON object.\n"
        f"{describe(schema)}",
        grounded(schema),
        system=GROUNDING_SYSTEM_PROMPT,
    )


def locate_text(client: OpenAI, image_url: str, text: str) -> list[int] | None:
    try:
        detections = ask(
            client,
            image_url,
            f'Provide bounding boxes for the text "{text}"',
            RootModel[conlist(Detection, max_length=MAX_DETECTIONS)],
            system=GROUNDING_SYSTEM_PROMPT,
        ).root
    except ValidationError:
        return None
    return detections[0].bbox_2d if detections else None


def main():
    client = OpenAI(base_url=VLLM_URL, api_key="unused")
    print(f"Model: {client.models.list().data[0].root}")
    for name, pdf_path, page_index, schema in TEST_CASES:
        with pdfium.PdfDocument(pdf_path) as pdf:
            page = pdf[page_index]
            image = render_page(page)
            image_url = to_data_url(image)
            print(f"\n## {name}: one grounded extraction call")
            try:
                result = extract_grounded(client, image_url, schema)
                report(page, image, result, OUTPUT_DIR / f"{name}.png")
            except ValidationError as error:
                print(f"extraction failed: {error.errors()[0]['msg']}")
            print(f"\n## {name}: extraction, then a grounding call per value")
            try:
                values = extract(client, image_url, schema)
            except ValidationError as error:
                print(f"extraction failed: {error.errors()[0]['msg']}")
                continue
            result = grounded(schema).model_validate(
                ground_values(client, image_url, values, locate_text)
            )
            report(page, image, result, OUTPUT_DIR / f"{name}_per_value.png")


if __name__ == "__main__":
    main()
