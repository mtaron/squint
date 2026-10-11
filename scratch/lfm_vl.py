"""The qwen_vl.py tests on LFM2.5-VL-450M, whose boxes are normalized to [0, 1]: one
description-guided extraction per page, and on the title page the model card's own detection
prompt per field. Run `task vllm` first to forward the server."""

import json
from pathlib import Path
from typing import Any, Literal, get_origin

import pypdfium2 as pdfium
from openai import OpenAI
from pydantic import BaseModel, RootModel, TypeAdapter, conlist, constr

from qwen_vl import (
    BOX_SCALE,
    TEST_CASES,
    VLLM_URL,
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

UnitBox = conlist(float, min_length=4, max_length=4)


class LfmGrounded(BaseModel):
    text: constr(min_length=1)
    bbox: UnitBox


def ask[T: BaseModel](
    client: OpenAI, image_url: str, prompt: str, schema: type[T]
) -> T:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        # The model card's text sampling settings
        temperature=0.1,
        max_tokens=4096,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "output", "schema": schema.model_json_schema()},
        },
        extra_body={"min_p": 0.15, "repetition_penalty": 1.05},
    )
    return schema.model_validate_json(response.choices[0].message.content)


def to_qwen_boxes(value: Any) -> Any:
    """Rescale [0, 1] boxes to Qwen's 0-1000 bbox_2d so qwen_vl's report applies."""
    if isinstance(value, dict) and "bbox" in value:
        return {
            "text": value["text"],
            "bbox_2d": [round(coordinate * BOX_SCALE) for coordinate in value["bbox"]],
        }
    if isinstance(value, dict):
        return {key: to_qwen_boxes(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_qwen_boxes(item) for item in value]
    return value


def extract(client: OpenAI, image_url: str, schema: type[BaseModel]) -> BaseModel:
    result = ask(
        client,
        image_url,
        "Extract the fields described by this JSON schema from the document: "
        f"{json.dumps(schema.model_json_schema())}. For each value, give its text exactly "
        "as printed and its bbox [x1, y1, x2, y2]. Coordinates are normalized to [0,1].",
        grounded(schema, LfmGrounded),
    )
    return grounded(schema).model_validate(to_qwen_boxes(result.model_dump()))


def detect_fields(client: OpenAI, image_url: str, schema: type[BaseModel]) -> BaseModel:
    """The detection prompt per field. It returns boxes only, so each value's text is a
    placeholder naming the query; the report shows the PDF text inside each box."""
    result = grounded(schema)
    fields = {}
    for name, field in schema.model_fields.items():
        query = field.title or name

        class Detection(BaseModel):
            label: Literal[query]
            bbox: UnitBox

        detections = ask(
            client,
            image_url,
            DETECTION_PROMPT.format(query=query),
            RootModel[list[Detection]],
        ).root
        values = [{"text": f"<{query}>", "bbox": d.bbox} for d in detections]
        if get_origin(field.annotation) is not list:
            if not values:
                print(f"{name:<20} nothing detected for {query!r}")
                continue
            values = values[0]
        fields[name] = TypeAdapter(
            result.model_fields[name].annotation
        ).validate_python(to_qwen_boxes(values))
    return result.model_construct(**fields)


def main():
    client = OpenAI(base_url=VLLM_URL, api_key="unused")
    print(f"Model: {client.models.list().data[0].root}")
    for name, pdf_path, page_index, schema in TEST_CASES:
        with pdfium.PdfDocument(pdf_path) as pdf:
            page = pdf[page_index]
            image = render_page(page)
            image_url = to_data_url(image)
            print(f"\n## {name}: extraction")
            report(
                page,
                image,
                extract(client, image_url, schema),
                OUTPUT_DIR / f"{name}.png",
            )
            if schema is Paper:
                print(f"\n## {name}: detection prompt per field")
                report(
                    page,
                    image,
                    detect_fields(client, image_url, schema),
                    OUTPUT_DIR / f"{name}_detection.png",
                )


if __name__ == "__main__":
    main()
