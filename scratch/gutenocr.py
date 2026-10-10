"""Extract a schema's fields from a page with GutenOCR and ground them in its OCR lines.
Run `task vllm` first to forward the server.

GutenOCR's OCR tasks don't cover schema fields, so the values come from what remains of
Qwen2.5-VL's instruction following (under its default system prompt). Each value is then
located by matching it against the line-level reading, the task GutenOCR was trained for."""

import base64
import json
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import cv2
import numpy as np
import pypdfium2 as pdfium
from openai import OpenAI
from pydantic import BaseModel, Field, TypeAdapter, conlist, constr
from transformers.models.qwen2_vl.image_processing_qwen2_vl import smart_resize

PDF_PATH = (
    Path(__file__).parent.parent
    / "datasets/vidore/vidore_v3_computer_science/pdfs/Introduction_to_Python_Programming.pdf"
)
PAGE_INDEX = 2
OVERLAY_PATH = Path(__file__).parent / "out" / "gutenocr.png"
VLLM_URL = "http://localhost:8000/v1"
MODEL = "gutenocr"

# GutenOCR was trained on pages rasterized at 72 dpi.
TRAINING_DPI = 72
# The server's --mm-processor-kwargs cap; pages within it reach the model unscaled.
MAX_PIXELS = 1003520
# Replaces the OCR system prompt the chat template injects, which steers every request
# toward a line dump.
QWEN_SYSTEM_PROMPT = "You are a helpful assistant."
# A value may wrap across lines (a two-line title) but shouldn't span a whole column.
MAX_SPAN_LINES = 4
MIN_COVERAGE = 0.9

Box = conlist(int, min_length=4, max_length=4)
FIELD_COLORS = [(255, 0, 0), (0, 128, 255), (0, 160, 0), (200, 0, 200)]


class Paper(BaseModel):
    title: str = Field(description="The document's title")
    authors: list[constr(min_length=1)] = Field(description="Each author's name")


class Line(BaseModel):
    text: str
    bbox: Box


class Grounded(BaseModel):
    text: str
    bbox: Box | None


LINES = TypeAdapter(list[Line])
GROUNDED_FIELDS = TypeAdapter(dict[str, Grounded | list[Grounded]])


def render_page(page: pdfium.PdfPage) -> np.ndarray:
    """RGB render at the training dpi, resized to the patch grid the model sees so its
    box coordinates are pixels of this image."""
    image = page.render(scale=TRAINING_DPI / 72, rev_byteorder=True).to_numpy()
    height, width = smart_resize(image.shape[0], image.shape[1], max_pixels=MAX_PIXELS)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def to_data_url(image: np.ndarray) -> str:
    _, png = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return f"data:image/png;base64,{base64.b64encode(png).decode()}"


def ask(
    client: OpenAI,
    image_url: str,
    prompt: str,
    schema: dict,
    system: str | None = None,
    max_tokens: int = 1024,
) -> str:
    messages = [{"role": "system", "content": system}] if system else []
    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt},
            ],
        }
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "output", "schema": schema},
        },
    )
    return response.choices[0].message.content or ""


def read_lines(client: OpenAI, image_url: str, width: int, height: int) -> list[Line]:
    content = ask(
        client,
        image_url,
        "Recognize all text in the document and return it as a JSON array of LINES and their bounding boxes.",
        LINES.json_schema(),
        max_tokens=8192,
    )
    lines = []
    for line in LINES.validate_json(content):
        x1, y1, x2, y2 = line.bbox
        x1, x2 = (min(max(x, 0), width) for x in (x1, x2))
        y1, y2 = (min(max(y, 0), height) for y in (y1, y2))
        if x1 < x2 and y1 < y2:
            lines.append(Line(text=line.text, bbox=[x1, y1, x2, y2]))
    return lines


def extract_values(client: OpenAI, image_url: str) -> Paper:
    schema = Paper.model_json_schema()
    content = ask(
        client,
        image_url,
        f"Extract the following fields from the document and return them as JSON matching this schema: {json.dumps(schema)}",
        schema,
        system=QWEN_SYSTEM_PROMPT,
    )
    return Paper.model_validate_json(content)


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def coverage(value: str, text: str) -> float:
    """Fraction of the value's characters that appear, in order, in the text."""
    matcher = SequenceMatcher(None, value, text, autojunk=False)
    return sum(block.size for block in matcher.get_matching_blocks()) / len(value)


def ground(value: str, lines: list[Line]) -> Grounded:
    """Box the shortest run of consecutive lines that covers the value."""
    target = normalize(value)
    if not target:
        return Grounded(text=value, bbox=None)
    spans = [
        lines[start:end]
        for start in range(len(lines))
        for end in range(start + 1, min(start + MAX_SPAN_LINES, len(lines)) + 1)
    ]
    scored = [
        (coverage(target, text), -len(text), span)
        for span in spans
        if (text := normalize(" ".join(line.text for line in span)))
    ]
    score, _, span = max(
        scored, key=lambda scored_span: scored_span[:2], default=(0, 0, [])
    )
    if score < MIN_COVERAGE:
        return Grounded(text=value, bbox=None)
    x1s, y1s, x2s, y2s = zip(*(line.bbox for line in span))
    return Grounded(text=value, bbox=[min(x1s), min(y1s), max(x2s), max(y2s)])


def extract(client: OpenAI, image: np.ndarray) -> dict[str, Grounded | list[Grounded]]:
    image_url = to_data_url(image)
    height, width = image.shape[:2]
    lines = read_lines(client, image_url, width, height)
    values = extract_values(client, image_url)
    return {
        name: [ground(item, lines) for item in value]
        if isinstance(value, list)
        else ground(value, lines)
        for name, value in values
    }


def pdf_text(
    page: pdfium.PdfPage,
    textpage: pdfium.PdfTextPage,
    box: list[int],
    image: np.ndarray,
) -> str:
    """The PDF text layer inside a box given in image pixels, for checking the model."""
    page_width, page_height = page.get_size()
    scale_x, scale_y = page_width / image.shape[1], page_height / image.shape[0]
    x1, y1, x2, y2 = box
    text = textpage.get_text_bounded(
        left=x1 * scale_x,
        bottom=page_height - y2 * scale_y,
        right=x2 * scale_x,
        top=page_height - y1 * scale_y,
    )
    return " ".join(text.split())


def save_overlay(image: np.ndarray, fields: dict[str, list[Grounded]]) -> None:
    overlay = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    for (name, grounded), color in zip(fields.items(), FIELD_COLORS):
        for item in grounded:
            if item.bbox is None:
                continue
            x1, y1, x2, y2 = item.bbox
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 1)
            cv2.putText(
                overlay,
                name,
                (x1, max(y1 - 3, 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
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
        fields = extract(client, image)

        as_lists = {
            name: value if isinstance(value, list) else [value]
            for name, value in fields.items()
        }
        textpage = page.get_textpage()
        for name, grounded in as_lists.items():
            for item in grounded:
                print(f"{name} {item.bbox}")
                print(f"  model: {item.text!r}")
                if item.bbox is None:
                    print("  pdf:   (not found in the OCR lines)")
                else:
                    print(f"  pdf:   {pdf_text(page, textpage, item.bbox, image)!r}")
    save_overlay(image, as_lists)
    print(f"Overlay saved to {OVERLAY_PATH}")
    print(GROUNDED_FIELDS.dump_json(fields, indent=2).decode())


if __name__ == "__main__":
    main()
