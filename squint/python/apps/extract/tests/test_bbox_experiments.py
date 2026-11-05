"""Bounding-box prompt experiments against the VLM.

Skipped unless VLLM_URL is set. With Tilt forwarding the VLM:

    VLLM_URL=http://localhost:8000/v1 uv run pytest tests/test_bbox_experiments.py -s

Every page and prompt pair leaves an image with the boxes drawn on the page and a JSON file with
the raw replies, in experiments/bbox/ at the repository root (outside the worker's build context,
so runs don't trigger a Tilt sync). A prompt that doesn't name a coordinate system has its boxes
drawn under every reading that fits the numbers, one color each.
"""

import base64
import json
import math
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from openai import OpenAI, omit
from openai.types.shared_params import ResponseFormatJSONSchema
from PIL import Image, ImageDraw, ImageFont

from activities import VLM_MODEL, Occurrences, locate_prompt

FIXTURES = Path(__file__).parent / "fixtures"
REPOSITORY = Path(__file__).parents[5]
OUTPUT = Path(os.environ.get("BBOX_OUTPUT", REPOSITORY / "experiments" / "bbox"))

# Printed text on each page, from easy (headings) to hard (single cells, rotated labels, footnotes)
TARGETS = {
    "stock-performance.jpg": ["58,273", "152.4", "PERFORMANCE GRAPH"],
    "adverse-event-reports.jpg": ["1,727,478", "1,971,272", "20 November 2018"],
    "generic-applications.jpg": [
        "25",
        "OGD has a robust, high quality process for filing review",
        "7/31/2018",
    ],
    "jack-maintenance.jpg": [
        "retracted position",
        "do not grease the rack teeth",
        "TM 9-243",
    ],
}

# The server's image processor, from --mm-processor-kwargs in infrastructure/helmfile.yaml.gotmpl:
# each side becomes a multiple of 32 px, and the area stays within these bounds
PATCH_FACTOR = 32
MIN_PIXELS = 65_536
MAX_PIXELS = 4_194_304

MAX_TOKENS = 512


def seen_size(width: int, height: int) -> tuple[int, int]:
    """The size the model sees a page at, following Qwen's smart_resize."""
    seen_width = round(width / PATCH_FACTOR) * PATCH_FACTOR
    seen_height = round(height / PATCH_FACTOR) * PATCH_FACTOR
    if seen_width * seen_height > MAX_PIXELS:
        beta = math.sqrt(width * height / MAX_PIXELS)
        seen_width = math.floor(width / beta / PATCH_FACTOR) * PATCH_FACTOR
        seen_height = math.floor(height / beta / PATCH_FACTOR) * PATCH_FACTOR
    elif seen_width * seen_height < MIN_PIXELS:
        beta = math.sqrt(MIN_PIXELS / (width * height))
        seen_width = math.ceil(width * beta / PATCH_FACTOR) * PATCH_FACTOR
        seen_height = math.ceil(height * beta / PATCH_FACTOR) * PATCH_FACTOR
    return seen_width, seen_height


def json_schema(name: str, schema: dict[str, Any]) -> ResponseFormatJSONSchema:
    return {
        "type": "json_schema",
        "json_schema": {"name": name, "schema": schema, "strict": True},
    }


# Named "bbox" rather than Qwen's "bbox_2d", and typed as numbers, so neither hints at a scale
UNSCALED_BOX = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "bbox": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 4,
            "maxItems": 4,
        },
    },
    "required": ["text", "bbox"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class Prompt:
    name: str
    text: Callable[[str], str]
    response_format: ResponseFormatJSONSchema | None = None
    # The readings to draw; every plausible one when the prompt doesn't name a scale
    readings: tuple[str, ...] | None = None


def bare_prompt(target: str) -> str:
    return f"Find the text {json.dumps(target)} on this page and give its bounding box."


def qwen_grounding_prompt(target: str) -> str:
    return f"Locate {json.dumps(target)} in the image, output its bbox coordinates using JSON format."


PROMPTS = [
    Prompt("bare", bare_prompt),
    Prompt("bare-json", bare_prompt, json_schema("box", UNSCALED_BOX)),
    Prompt("qwen-grounding", qwen_grounding_prompt),
    Prompt(
        "production",
        locate_prompt,
        json_schema("occurrences", Occurrences.model_json_schema()),
        readings=("0-1000",),
    ),
]

NUMBER = r"\s*(-?\d+(?:\.\d+)?)\s*"
QUADRUPLE = re.compile(r"[\[(]" + ",".join([NUMBER] * 4) + r"[\])]")


def parse_boxes(reply: str) -> list[tuple[float, float, float, float]]:
    """Every [x1, y1, x2, y2] or (x1, y1, x2, y2) in a reply, whatever surrounds it."""
    return [
        (float(x1), float(y1), float(x2), float(y2))
        for x1, y1, x2, y2 in QUADRUPLE.findall(reply)
    ]


@dataclass(frozen=True)
class Reading:
    name: str
    color: str
    # Multipliers from the reply's numbers to page pixels
    scale_x: float
    scale_y: float
    # The largest x and y the reading allows
    max_x: float
    max_y: float

    def fits(self, box: tuple[float, float, float, float]) -> bool:
        x1, y1, x2, y2 = box
        return all(0 <= value <= self.max_x for value in (x1, x2)) and all(
            0 <= value <= self.max_y for value in (y1, y2)
        )

    def to_page(
        self, box: tuple[float, float, float, float]
    ) -> tuple[float, float, float, float]:
        x1, y1, x2, y2 = box
        return (
            min(x1, x2) * self.scale_x,
            min(y1, y2) * self.scale_y,
            max(x1, x2) * self.scale_x,
            max(y1, y2) * self.scale_y,
        )


def readings(page: Image.Image) -> list[Reading]:
    width, height = page.size
    seen_width, seen_height = seen_size(width, height)
    return [
        Reading("0-1000", "#e6194b", width / 1000, height / 1000, 1000, 1000),
        Reading("0-1", "#4363d8", width, height, 1, 1),
        Reading(
            f"pixels of {seen_width}x{seen_height}",
            "#3cb44b",
            width / seen_width,
            height / seen_height,
            seen_width,
            seen_height,
        ),
    ]


@dataclass
class Result:
    target: str
    reply: str
    boxes: list[tuple[float, float, float, float]]
    usage: dict[str, Any] | None
    drawn: dict[str, list[tuple[float, float, float, float]]] = field(
        default_factory=dict
    )


def ask(vlm: OpenAI, image_url: str, prompt: Prompt, target: str) -> Result:
    response = vlm.chat.completions.create(
        model=VLM_MODEL,
        temperature=0,
        max_tokens=MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt.text(target)},
                ],
            }
        ],
        response_format=prompt.response_format or omit,
    )
    reply = response.choices[0].message.content or ""
    return Result(
        target=target,
        reply=reply,
        boxes=parse_boxes(reply),
        usage=response.usage.model_dump() if response.usage else None,
    )


def draw(page: Image.Image, prompt: Prompt, results: list[Result]) -> Image.Image:
    canvas = page.convert("RGB")
    pen = ImageDraw.Draw(canvas)
    font_size = max(18, page.height // 80)
    font = ImageFont.load_default(size=font_size)
    candidates = [
        reading
        for reading in readings(page)
        if prompt.readings is None or reading.name in prompt.readings
    ]
    used: set[str] = set()
    for result in results:
        for box in result.boxes:
            for reading in candidates:
                if not reading.fits(box):
                    continue
                corners = reading.to_page(box)
                result.drawn.setdefault(reading.name, []).append(corners)
                used.add(reading.name)
                pen.rectangle(corners, outline=reading.color, width=4)
                pen.text(
                    (corners[0], corners[1] - font_size - 4),
                    result.target,
                    fill=reading.color,
                    font=font,
                )

    legend = [
        (reading.name, reading.color) for reading in candidates if reading.name in used
    ]
    missing = [result.target for result in results if not result.boxes]
    if missing:
        legend.append(("no box parsed: " + ", ".join(missing), "#000000"))
    for line, (label, color) in enumerate(legend):
        pen.text((10, 10 + line * (font_size + 6)), label, fill=color, font=font)
    return canvas


pytestmark = pytest.mark.skipif(
    "VLLM_URL" not in os.environ,
    reason="set VLLM_URL to run the bounding-box experiments against the VLM",
)


@pytest.fixture(scope="module")
def vlm() -> OpenAI:
    return OpenAI(base_url=os.environ["VLLM_URL"], api_key="unused", max_retries=0)


@pytest.mark.parametrize("prompt", PROMPTS, ids=lambda prompt: prompt.name)
@pytest.mark.parametrize("page_name", TARGETS, ids=lambda name: Path(name).stem)
def test_draws_the_boxes_the_vlm_returns(
    vlm: OpenAI, page_name: str, prompt: Prompt
) -> None:
    path = FIXTURES / page_name
    image_url = "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()
    page = Image.open(path)
    results = [ask(vlm, image_url, prompt, target) for target in TARGETS[page_name]]

    out_dir = OUTPUT / prompt.name
    out_dir.mkdir(parents=True, exist_ok=True)
    image_path = out_dir / f"{path.stem}.png"
    draw(page, prompt, results).save(image_path)
    (out_dir / f"{path.stem}.json").write_text(
        json.dumps(
            {
                "page": page_name,
                "page_size": page.size,
                "seen_size": seen_size(*page.size),
                "prompt": prompt.name,
                "results": [result.__dict__ for result in results],
            },
            indent=2,
        )
    )

    print(f"\n{prompt.name} / {path.stem}: {image_path.as_uri()}")
    for result in results:
        print(
            f"  {result.target!r}: {result.boxes or 'no box'}  <- {result.reply[:200]!r}"
        )

    assert all(result.reply for result in results), "the VLM returned an empty reply"
