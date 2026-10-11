"""The qwen_vl.py extraction on Claude Haiku 5.5, kept to as few tokens as the API allows.
Needs ANTHROPIC_API_KEY (or an `ant auth login` profile)."""

import base64
from pathlib import Path

import anthropic
import cv2
import numpy as np
import pypdfium2 as pdfium
from pydantic import BaseModel, conlist, constr

from qwen_vl import BOX_SCALE, PAGE_INDEX, PDF_PATH, Paper, grounded, pdf_text

MODEL = "claude-haiku-5-5"
OVERLAY_PATH = Path(__file__).parent / "out" / "haiku_vl.png"
# Image tokens grow with area (about width x height / 750); the title page stays legible
# at 72 dpi, and an image this small reaches the model unscaled, so pixel boxes line up.
RENDER_DPI = 72
# US dollars per million tokens, for prompts up to 100K tokens
INPUT_PRICE = 0.10
OUTPUT_PRICE = 0.50


class PixelGrounded(BaseModel):
    text: constr(min_length=1)
    bbox: conlist(int, min_length=4, max_length=4)


PixelPaper = grounded(Paper, PixelGrounded)


def render_page(page: pdfium.PdfPage) -> np.ndarray:
    return page.render(scale=RENDER_DPI / 72, rev_byteorder=True).to_numpy()


def extract(
    client: anthropic.Anthropic, image: np.ndarray
) -> tuple[BaseModel, anthropic.types.Usage]:
    height, width = image.shape[:2]
    _, png = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    response = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        # Disabling thinking is accepted at effort high or below; low also keeps replies terse.
        thinking={"type": "disabled"},
        output_config={"effort": "low"},
        # The field descriptions reach the model through the schema, so the prompt stays short.
        output_format=PixelPaper,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64.standard_b64encode(png).decode(),
                        },
                    },
                    {
                        "type": "text",
                        "text": f"Extract the fields, copying text exactly as printed, capitalization included. bbox is [x1, y1, x2, y2] in pixels of this {width}x{height} image.",
                    },
                ],
            }
        ],
    )
    if response.stop_reason != "end_turn" or response.parsed_output is None:
        raise RuntimeError(
            f"No extraction: stop_reason={response.stop_reason} {response.stop_details}"
        )
    return response.parsed_output, response.usage


def to_relative(box: list[int], width: int, height: int) -> list[int]:
    x1, y1, x2, y2 = box
    return [
        round(x1 * BOX_SCALE / width),
        round(y1 * BOX_SCALE / height),
        round(x2 * BOX_SCALE / width),
        round(y2 * BOX_SCALE / height),
    ]


def save_overlay(image: np.ndarray, fields: dict[str, list[PixelGrounded]]) -> None:
    overlay = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    colors = [(255, 0, 0), (0, 128, 255), (0, 160, 0), (200, 0, 200)]
    for (name, values), color in zip(fields.items(), colors):
        for value in values:
            x1, y1, x2, y2 = value.bbox
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
    client = anthropic.Anthropic()
    with pdfium.PdfDocument(PDF_PATH) as pdf:
        page = pdf[PAGE_INDEX]
        image = render_page(page)
        height, width = image.shape[:2]
        result, usage = extract(client, image)

        fields = {
            name: value if isinstance(value, list) else [value]
            for name, value in result
        }
        textpage = page.get_textpage()
        for name, values in fields.items():
            for value in values:
                relative = to_relative(value.bbox, width, height)
                print(f"{name} {value.bbox}")
                print(f"  model: {value.text!r}")
                print(f"  pdf:   {pdf_text(page, textpage, relative)!r}")
    save_overlay(image, fields)
    print(f"Overlay saved to {OVERLAY_PATH}")
    cost = (usage.input_tokens * INPUT_PRICE + usage.output_tokens * OUTPUT_PRICE) / 1e6
    print(f"Tokens: {usage.input_tokens} in, {usage.output_tokens} out (${cost:.6f})")


if __name__ == "__main__":
    main()
