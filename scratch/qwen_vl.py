"""Extract schemas from pages with Qwen VL, with the text and bounding box of each value: a
title page, two reference lists in different citation styles, and cells of a table with
two-level column headers. Each page runs one description-guided extraction call; the title
page also runs Qwen's own grounding prompt, one call per field. Run `task vllm` first to
forward the server."""

import base64
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Literal, get_args, get_origin

import cv2
import numpy as np
import pypdfium2 as pdfium
from openai import OpenAI
from pydantic import BaseModel, Field, RootModel, conlist, constr, create_model

DATASETS_DIR = Path(__file__).parent.parent / "datasets/vidore"
PDF_PATH = (
    DATASETS_DIR
    / "vidore_v3_computer_science/pdfs/Introduction_to_Python_Programming.pdf"
)
PAGE_INDEX = 2
OUTPUT_DIR = Path(__file__).parent / "out"
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


class Citation(BaseModel):
    title: str = Field(
        description="The title of the cited work only, without its authors, year, venue or URL"
    )
    year: str = Field(description="The year the cited work was published")


class Citations(BaseModel):
    citations: list[Citation] = Field(
        description="Every entry in the reference list, in order"
    )


class Deposits(BaseModel):
    time_2023_average_amount: str = Field(
        description="The 2023 average amount of time deposits, in $ millions"
    )
    total_2022_average_rate: str = Field(
        description="The 2022 average rate on total deposits"
    )
    savings_and_demand_2024_average_rate: str = Field(
        description="The 2024 average rate on savings and demand deposits"
    )


# (name, PDF, page index, schema)
TEST_CASES = [
    ("title_page", PDF_PATH, PAGE_INDEX, Paper),
    # Chicago author-date: unquoted titles mid-entry; articles, books and web pages
    (
        "citations_chicago",
        DATASETS_DIR / "vidore_v3_pharmaceuticals/pdfs/drug_resistance_book.pdf",
        149,
        Citations,
    ),
    # Year in parentheses, quoted titles
    (
        "citations_quoted",
        DATASETS_DIR
        / "vidore_v3_hr/pdfs/employment_and_social_developments_in_europe_2024-KEBD24002ENN.pdf",
        108,
        Citations,
    ),
    # Each year spans an average amount and an average rate column
    (
        "table_cells",
        DATASETS_DIR / "vidore_v3_finance_en/pdfs/morgan_stanley_2024.pdf",
        150,
        Deposits,
    ),
]


class Grounded(BaseModel):
    text: constr(min_length=1)
    bbox_2d: Box


def grounded(
    schema: type[BaseModel], value: type[BaseModel] = Grounded
) -> type[BaseModel]:
    """The schema with each string value replaced by its text and bounding box."""

    def convert(annotation: Any) -> Any:
        if get_origin(annotation) is list:
            return list[convert(get_args(annotation)[0])]
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return grounded(annotation, value)
        return value

    fields = {
        name: (convert(field.annotation), Field(description=field.description))
        for name, field in schema.model_fields.items()
    }
    return create_model(f"Grounded{schema.__name__}", **fields)


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
        temperature=0,
        max_tokens=8192,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "output", "schema": schema.model_json_schema()},
        },
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    return schema.model_validate_json(response.choices[0].message.content)


def extract(client: OpenAI, image: np.ndarray, schema: type[BaseModel]) -> BaseModel:
    """One call: the schema with its descriptions, each value returned with its box."""
    return ask(
        client,
        to_data_url(image),
        "Extract the fields described by this JSON schema from the document: "
        f"{json.dumps(schema.model_json_schema())}. For each value, give its text exactly "
        f"as printed and its bbox_2d [x1, y1, x2, y2] relative to the image, from 0 to {BOX_SCALE}.",
        grounded(schema),
    )


def union(boxes: list[list[int]]) -> list[int]:
    x1s, y1s, x2s, y2s = zip(*boxes)
    return [min(x1s), min(y1s), max(x2s), max(y2s)]


def locate_fields(
    client: OpenAI, image: np.ndarray, schema: type[BaseModel]
) -> BaseModel:
    """Qwen's grounding prompt, one call per field of a flat schema, as each field will
    follow its own retrieval step."""
    image_url = to_data_url(image)
    fields = {}
    for name, field in schema.model_fields.items():
        category = field.title or name
        instances = ask(
            client,
            image_url,
            GROUNDING_PROMPT.format(category=category),
            instances_schema(category),
        ).root
        matches = [
            Grounded(text=instance.text_content, bbox_2d=instance.bbox_2d)
            for instance in instances
        ]
        if get_origin(field.annotation) is list:
            fields[name] = matches
        elif matches:
            fields[name] = Grounded(
                text=" ".join(match.text for match in matches),
                bbox_2d=union([match.bbox_2d for match in matches]),
            )
        else:
            print(f"{name:<20} nothing located for {category!r}")
    return grounded(schema).model_construct(**fields)


def leaves(value: Any, path: str = "") -> Iterator[tuple[str, Grounded]]:
    """Each grounded value in a result, with its path, e.g. citations[3].title."""
    if isinstance(value, Grounded):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from leaves(item, f"{path}[{index}]")
    elif isinstance(value, BaseModel):
        for name, item in value:
            yield from leaves(item, f"{path}.{name}" if path else name)


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


def save_overlay(image: np.ndarray, result: BaseModel, path: Path) -> None:
    overlay = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    height, width = image.shape[:2]
    colors = dict(zip(type(result).model_fields, FIELD_COLORS * 4))
    for leaf_path, value in leaves(result):
        color = colors[leaf_path.split(".")[0].split("[")[0]]
        x1, y1, x2, y2 = to_pixels(value.bbox_2d, width, height)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
    path.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(path), overlay)


def report(
    page: pdfium.PdfPage, image: np.ndarray, result: BaseModel, overlay_path: Path
) -> None:
    textpage = page.get_textpage()
    for path, value in leaves(result):
        print(f"{path:<20} {value.text!r}")
        print(f"{'':<20} pdf: {pdf_text(page, textpage, value.bbox_2d)!r}")
    save_overlay(image, result, overlay_path)


def main():
    client = OpenAI(base_url=VLLM_URL, api_key="unused")
    print(f"Model: {client.models.list().data[0].root}")
    for name, pdf_path, page_index, schema in TEST_CASES:
        with pdfium.PdfDocument(pdf_path) as pdf:
            page = pdf[page_index]
            image = render_page(page)
            print(f"\n## {name}: extraction")
            report(
                page, image, extract(client, image, schema), OUTPUT_DIR / f"{name}.png"
            )
            if schema is Paper:
                print(f"\n## {name}: grounding prompt per field")
                report(
                    page,
                    image,
                    locate_fields(client, image, schema),
                    OUTPUT_DIR / f"{name}_grounding.png",
                )


if __name__ == "__main__":
    main()
