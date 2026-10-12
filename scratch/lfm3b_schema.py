"""Schema shape against field descriptions on LFM2.5-VL-3B: author names as {first, last} and
nested citations, with generic descriptions (no document-specific hints such as "without
their affiliation"). Each page runs qwen_vl's schema prompt and lfm3b_vl's grounding-system-
prompt extraction; values are scored against the expected answers and boxes against the PDF
text layer. Run `task vllm` first to forward the server."""

import re
import unicodedata
from pathlib import Path

import pypdfium2 as pdfium
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

import qwen_vl
from lfm3b_vl import extract_grounded
from qwen_vl import (
    TEST_CASES,
    VLLM_URL,
    leaves,
    pdf_text,
    render_page,
    save_overlay,
    to_data_url,
)

qwen_vl.MODEL = "lfm-vl"
OUTPUT_DIR = Path(__file__).parent / "out" / "lfm-3b-schema"
# Every title in each reference list, from Qwen3.5-9B's correct answers
EXPECTED_RESULTS = Path(__file__).parent / "out" / "9b" / "results.txt"
AUTHORS = [
    ("UDAYAN", "DAS"),
    ("AUBREY", "LAWSON"),
    ("CHRIS", "MAYFIELD"),
    ("NARGES", "NOROUZI"),
]


class Name(BaseModel):
    first: str = Field(description="The person's first name")
    last: str = Field(description="The person's last name")


class AuthoredDocument(BaseModel):
    title: str = Field(description="The document's title")
    authors: list[Name] = Field(description="The document's authors")


class Citation(BaseModel):
    title: str = Field(description="The title of the cited work")
    year: str = Field(description="The year the cited work was published")


class Citations(BaseModel):
    citations: list[Citation] = Field(
        description="The works cited in the reference list"
    )


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKC", text).lower())


def expected_titles(section: str) -> set[str]:
    text = EXPECTED_RESULTS.read_text().split(f"## {section}")[1].split("\n## ")[0]
    return {
        norm(match.group(2))
        for match in re.finditer(
            r"""^citations\[\d+\]\.title\s+(['"])(.*)\1$""", text, re.MULTILINE
        )
    }


def score_values(name: str, result: BaseModel) -> str:
    if name == "title_page":
        names = [(author.first.text, author.last.text) for author in result.authors]
        correct = sum(
            (norm(first), norm(last)) in {(norm(f), norm(l)) for f, l in AUTHORS}
            for first, last in names
        )
        title_ok = norm(result.title.text) == norm("Introduction to Python Programming")
        return f"title {'correct' if title_ok else 'wrong'}; {correct}/{len(AUTHORS)} authors correct of {len(names)} returned: {names}"
    expected = expected_titles(name)
    titles = [citation.title.text for citation in result.citations]
    correct = sum(norm(title) in expected for title in titles)
    return f"{correct}/{len(expected)} titles exactly right of {len(titles)} returned; e.g. {titles[0][:70]!r}"


def score_boxes(page, textpage, result: BaseModel) -> str:
    values = list(leaves(result))
    hits = sum(
        norm(value.text)[:20] in norm(pdf_text(page, textpage, value.bbox_2d))
        for _, value in values
    )
    return f"{hits}/{len(values)} boxes contain their value"


def main():
    client = OpenAI(base_url=VLLM_URL, api_key="unused")
    print(f"Model: {client.models.list().data[0].root}")
    for name, pdf_path, page_index, _ in TEST_CASES[:3]:
        schema = AuthoredDocument if name == "title_page" else Citations
        with pdfium.PdfDocument(pdf_path) as pdf:
            page = pdf[page_index]
            textpage = page.get_textpage()
            image = render_page(page)
            image_url = to_data_url(image)
            for mode in ("qwen_vl schema prompt", "grounding system prompt"):
                print(f"\n## {name}: {mode}")
                try:
                    result = (
                        qwen_vl.extract(client, image, schema)
                        if mode.startswith("qwen_vl")
                        else extract_grounded(client, image_url, schema)
                    )
                except ValidationError as error:
                    print(f"  extraction failed: {error.errors()[0]['msg']}")
                    continue
                print(f"  values: {score_values(name, result)}")
                print(f"  boxes:  {score_boxes(page, textpage, result)}")
                save_overlay(
                    image, result, OUTPUT_DIR / f"{name}_{mode.split()[0]}.png"
                )


if __name__ == "__main__":
    main()
