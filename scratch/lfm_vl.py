"""The qwen_vl.py tests on LFM2.5-VL, following Liquid's invoice-parser cookbook: a
plain-language request listing each field's description, then each extracted value located
with the model card's detection prompt in its own call. The title page also runs the detection
prompt per field. Boxes are normalized to [0, 1]. Run `task vllm` first to forward the
server; set LFM_GROUNDING_URL to ground with a second server (e.g. the 450M while the 1.6B
extracts)."""

import os
from pathlib import Path
from typing import Any, Literal, get_args, get_origin

import pypdfium2 as pdfium
from openai import OpenAI
from pydantic import BaseModel, RootModel, ValidationError, confloat, conlist

from qwen_vl import (
    BOX_SCALE,
    TEST_CASES,
    VLLM_URL,
    Grounded,
    Paper,
    grounded,
    render_page,
    report,
    to_data_url,
)

MODEL = "lfm-vl"
OUTPUT_DIR = Path(__file__).parent / "out" / "lfm"
# The model card's grounding prompt
DETECTION_PROMPT = (
    "Detect all instances of: {query}. Response must be a JSON array: "
    '[{{"label": ..., "bbox": [x1, y1, x2, y2]}}, ...]. Coordinates are normalized to [0,1].'
)

UnitBox = conlist(confloat(ge=0, le=1), min_length=4, max_length=4)
# Keeps a detection that never stops from running to the token limit
MAX_DETECTIONS = 10


def ask[T: BaseModel](
    client: OpenAI, image_url: str, prompt: str, schema: type[T]
) -> T:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                # The cookbook puts the request before the image
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=0,
        max_tokens=4096,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "output", "schema": schema.model_json_schema()},
        },
    )
    return schema.model_validate_json(response.choices[0].message.content)


def describe(schema: type[BaseModel], indent: str = "") -> str:
    """The schema's fields and descriptions as plain-language lines, as in the cookbook."""
    lines = []
    for name, field in schema.model_fields.items():
        lines.append(f"{indent}{name}: {field.description}.")
        item = (
            get_args(field.annotation)[0]
            if get_origin(field.annotation) is list
            else None
        )
        if isinstance(item, type) and issubclass(item, BaseModel):
            lines.append(f"{indent}Each item in {name} has:")
            lines.append(describe(item, indent + "  "))
    return "\n".join(lines)


def extract[T: BaseModel](client: OpenAI, image_url: str, schema: type[T]) -> T:
    return ask(
        client,
        image_url,
        "Extract the following from the document, copying text exactly as printed. "
        f"Present as a JSON object.\n{describe(schema)}",
        schema,
    )


def detect(client: OpenAI, image_url: str, query: str) -> list[list[float]]:
    class Detection(BaseModel):
        label: Literal[query]
        bbox: UnitBox

    try:
        detections = ask(
            client,
            image_url,
            DETECTION_PROMPT.format(query=query),
            RootModel[conlist(Detection, max_length=MAX_DETECTIONS)],
        ).root
    except ValidationError:
        return []
    return [detection.bbox for detection in detections]


def to_box_2d(bbox: list[float]) -> list[int]:
    return [round(coordinate * BOX_SCALE) for coordinate in bbox]


def ground_values(client: OpenAI, image_url: str, value: Any) -> Any:
    """Each extracted string located as the text it is; [0, 0, 0, 0] when not detected."""
    if isinstance(value, str):
        boxes = detect(client, image_url, f'the text "{value}"')
        return Grounded(
            text=value or "<empty>",
            bbox_2d=to_box_2d(boxes[0]) if boxes else [0, 0, 0, 0],
        )
    if isinstance(value, list):
        return [ground_values(client, image_url, item) for item in value]
    return {name: ground_values(client, image_url, item) for name, item in value}


def detect_fields(client: OpenAI, image_url: str, schema: type[BaseModel]) -> BaseModel:
    """The detection prompt per field. It returns boxes only, so each value's text is a
    placeholder naming the query; the report shows the PDF text inside each box."""
    fields = {}
    for name, field in schema.model_fields.items():
        query = field.title or name
        values = [
            Grounded(text=f"<{query}>", bbox_2d=to_box_2d(bbox))
            for bbox in detect(client, image_url, query)
        ]
        if get_origin(field.annotation) is list:
            fields[name] = values
        elif values:
            fields[name] = values[0]
        else:
            print(f"{name:<20} nothing detected for {query!r}")
    return grounded(schema).model_construct(**fields)


def main():
    client = OpenAI(base_url=VLLM_URL, api_key="unused")
    grounding_client = OpenAI(
        base_url=os.environ.get("LFM_GROUNDING_URL", VLLM_URL), api_key="unused"
    )
    print(
        f"Extraction: {client.models.list().data[0].root}"
        f" | grounding: {grounding_client.models.list().data[0].root}"
    )
    for name, pdf_path, page_index, schema in TEST_CASES:
        with pdfium.PdfDocument(pdf_path) as pdf:
            page = pdf[page_index]
            image = render_page(page)
            image_url = to_data_url(image)
            print(f"\n## {name}: extraction, then detection per value")
            try:
                values = extract(client, image_url, schema)
            except ValidationError as error:
                print(f"extraction failed: {error.errors()[0]['msg']}")
                continue
            result = grounded(schema).model_validate(
                ground_values(grounding_client, image_url, values)
            )
            report(page, image, result, OUTPUT_DIR / f"{name}.png")
            if schema is Paper:
                print(f"\n## {name}: detection prompt per field")
                report(
                    page,
                    image,
                    detect_fields(grounding_client, image_url, schema),
                    OUTPUT_DIR / f"{name}_detection.png",
                )


if __name__ == "__main__":
    main()
