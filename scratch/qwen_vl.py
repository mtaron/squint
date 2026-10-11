"""Extract a schema's fields from a page, with the text and bounding box of each value, using
Qwen's own grounding prompt in one call per field. Run `task vllm` first to forward the
server."""

import base64
from pathlib import Path
from typing import Literal, get_origin

import cv2
import numpy as np
import pypdfium2 as pdfium
from openai import OpenAI
from pydantic import BaseModel, Field, RootModel, conlist, constr, create_model

PDF_PATH = (
    Path(__file__).parent.parent
    / "datasets/vidore/vidore_v3_computer_science/pdfs/Introduction_to_Python_Programming.pdf"
)
PAGE_INDEX = 2
OVERLAY_PATH = Path(__file__).parent / "out" / "qwen_vl.png"
VLLM_URL = "http://localhost:8000/v1"
MODEL = "qwen-vl"

# A 144 dpi letter page fits the server's 2048 visual-token cap unscaled.
RENDER_DPI = 144
# Qwen3-VL and later report boxes relative to the image, scaled to 0-1000.
BOX_SCALE = 1000

Box = conlist(int, min_length=4, max_length=4)
FIELD_COLORS = [(255, 0, 0), (0, 128, 255), (0, 160, 0), (200, 0, 200)]


class Paper(BaseModel):
    # Each field's title is the category the grounding prompt asks Qwen to locate. The
    # wording matters: a bare "title" comes back empty, "author" returns whole lines.
    title: str = Field(title="document title", description="The document's title")
    authors: list[str] = Field(
        title="author name",
        description="The name of each person who wrote the document, without their affiliation",
    )


class Grounded(BaseModel):
    text: constr(min_length=1)
    bbox_2d: Box


def grounded(
    schema: type[BaseModel], value: type[BaseModel] = Grounded
) -> type[BaseModel]:
    """The schema with each string value replaced by its text and bounding box."""
    fields = {
        name: (
            list[value] if get_origin(field.annotation) is list else value,
            Field(description=field.description),
        )
        for name, field in schema.model_fields.items()
    }
    return create_model(f"Grounded{schema.__name__}", **fields)


GroundedPaper = grounded(Paper)


# Qwen3-VL cookbook grounding prompt (2d_grounding.ipynb, attribute variant), with the OCR
# cookbook's text_content key.
GROUNDING_PROMPT = (
    'Locate every instance that belongs to the following categories: "{category}". '
    "For each instance, report bbox coordinates and text content in JSON format like this: "
    '{{"bbox_2d": [x1, y1, x2, y2], "label": "category", "text_content": "text"}}'
)


def instances_schema(category: str) -> type[RootModel]:
    class Instance(BaseModel):
        bbox_2d: Box
        label: Literal[category]
        text_content: constr(min_length=1)

    return RootModel[list[Instance]]


def render_page(page: pdfium.PdfPage) -> np.ndarray:
    return page.render(scale=RENDER_DPI / 72, rev_byteorder=True).to_numpy()


def to_data_url(image: np.ndarray) -> str:
    _, png = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return f"data:image/png;base64,{base64.b64encode(png).decode()}"


def union(boxes: list[list[int]]) -> list[int]:
    x1s, y1s, x2s, y2s = zip(*boxes)
    return [min(x1s), min(y1s), max(x2s), max(y2s)]


def locate(client: OpenAI, image_url: str, category: str) -> list[Grounded]:
    schema = instances_schema(category)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {
                        "type": "text",
                        "text": GROUNDING_PROMPT.format(category=category),
                    },
                ],
            }
        ],
        temperature=0,
        max_tokens=2048,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "instances", "schema": schema.model_json_schema()},
        },
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    return [
        Grounded(text=instance.text_content, bbox_2d=instance.bbox_2d)
        for instance in schema.model_validate_json(
            response.choices[0].message.content
        ).root
    ]


def extract(client: OpenAI, image: np.ndarray) -> BaseModel:
    """One grounding call per field, as each field will follow its own retrieval step."""
    image_url = to_data_url(image)
    fields = {}
    for name, field in Paper.model_fields.items():
        matches = locate(client, image_url, field.title or name)
        if get_origin(field.annotation) is list:
            fields[name] = matches
        elif matches:
            fields[name] = Grounded(
                text=" ".join(match.text for match in matches),
                bbox_2d=union([match.bbox_2d for match in matches]),
            )
    return GroundedPaper(**fields)


def to_pixels(box: list[int], width: int, height: int) -> list[int]:
    x1, y1, x2, y2 = box
    return [
        round(x1 * width / BOX_SCALE),
        round(y1 * height / BOX_SCALE),
        round(x2 * width / BOX_SCALE),
        round(y2 * height / BOX_SCALE),
    ]


def pdf_text(page: pdfium.PdfPage, textpage: pdfium.PdfTextPage, box: list[int]) -> str:
    """The PDF text layer inside a relative box, for checking the model."""
    width, height = page.get_size()
    x1, y1, x2, y2 = (coordinate / BOX_SCALE for coordinate in box)
    text = textpage.get_text_bounded(
        left=x1 * width,
        bottom=height - y2 * height,
        right=x2 * width,
        top=height - y1 * height,
    )
    return " ".join(text.split())


def save_overlay(image: np.ndarray, fields: dict[str, list[Grounded]]) -> None:
    overlay = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    height, width = image.shape[:2]
    for (name, grounded_values), color in zip(fields.items(), FIELD_COLORS):
        for value in grounded_values:
            x1, y1, x2, y2 = to_pixels(value.bbox_2d, width, height)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                overlay,
                name,
                (x1, max(y1 - 5, 12)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                1,
            )
    OVERLAY_PATH.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(OVERLAY_PATH), overlay)


def main():
    client = OpenAI(base_url=VLLM_URL, api_key="unused")
    with pdfium.PdfDocument(PDF_PATH) as pdf:
        page = pdf[PAGE_INDEX]
        image = render_page(page)
        result = extract(client, image)

        fields = {
            name: value if isinstance(value, list) else [value]
            for name, value in result
        }
        textpage = page.get_textpage()
        for name, grounded_values in fields.items():
            for value in grounded_values:
                print(f"{name} {value.bbox_2d}")
                print(f"  model: {value.text!r}")
                print(f"  pdf:   {pdf_text(page, textpage, value.bbox_2d)!r}")
    save_overlay(image, fields)
    print(f"Overlay saved to {OVERLAY_PATH}")


if __name__ == "__main__":
    main()
