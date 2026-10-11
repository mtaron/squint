"""Key information extraction (KIE) with GLM-OCR: the page image plus a JSON template of the
schema, without the SDK's layout model. Runs the title page test and a citations test on two
reference pages in different styles. Run `task vllm` first to forward the server."""

import json
from pathlib import Path
from typing import Any, get_args, get_origin

import pypdfium2 as pdfium
from openai import OpenAI
from pydantic import BaseModel

from qwen_vl import PAGE_INDEX, PDF_PATH, Paper, to_data_url

DATASETS_DIR = Path(__file__).parent.parent / "datasets/vidore"
CITATION_PAGES = [
    # Chicago author-date: unquoted titles mid-entry; articles, books and web pages
    (
        DATASETS_DIR / "vidore_v3_pharmaceuticals/pdfs/drug_resistance_book.pdf",
        149,
    ),
    # Year in parentheses, quoted titles
    (
        DATASETS_DIR
        / "vidore_v3_hr/pdfs/employment_and_social_developments_in_europe_2024-KEBD24002ENN.pdf",
        108,
    ),
]
VLLM_URL = "http://localhost:8000/v1"
MODEL = "glm-ocr"
# The GLM-OCR SDK rasterizes PDFs at 200 dpi.
RENDER_DPI = 200
# The model card's KIE instruction ("Output the information in the image in the following
# JSON format:"); prompts must follow it strictly.
KIE_PROMPT = "请按下列JSON格式输出图中信息:\n{template}"


class Author(BaseModel):
    name: str
    affiliation: str


class KiePaper(BaseModel):
    """Paper as a KIE template. The model sees only the template's keys, so an affiliation key
    is what keeps affiliations out of the names, and items must be objects: a template list of
    N strings comes back with N items."""

    title: str
    authors: list[Author]


class Citation(BaseModel):
    title: str
    year: str


class Citations(BaseModel):
    citations: list[Citation]


def kie_template(annotation: Any) -> Any:
    """A schema as a KIE template: its keys with empty values, one item per list."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return {
            name: kie_template(field.annotation)
            for name, field in annotation.model_fields.items()
        }
    if get_origin(annotation) is list:
        return [kie_template(get_args(annotation)[0])]
    return ""


def extract[T: BaseModel](client: OpenAI, page: pdfium.PdfPage, schema: type[T]) -> T:
    image = page.render(scale=RENDER_DPI / 72, rev_byteorder=True).to_numpy()
    template = json.dumps(kie_template(schema), ensure_ascii=False, indent=4)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": to_data_url(image)}},
                    {"type": "text", "text": KIE_PROMPT.format(template=template)},
                ],
            }
        ],
        temperature=0,
        max_tokens=8192,
        # The SDK's repetition_penalty of 1.1 drops the comma after ~20 repeated list items,
        # leaving invalid JSON; the schema guards the rest.
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "schema": schema.model_json_schema(),
            },
        },
    )
    return schema.model_validate_json(response.choices[0].message.content)


def main():
    client = OpenAI(base_url=VLLM_URL, api_key="unused")

    print("## Title page")
    with pdfium.PdfDocument(PDF_PATH) as pdf:
        result = extract(client, pdf[PAGE_INDEX], KiePaper)
    paper = Paper(
        title=result.title, authors=[author.name for author in result.authors]
    )
    print(paper.model_dump_json(indent=2))

    for path, page_index in CITATION_PAGES:
        print(f"\n## Citations: {path.name} page {page_index}")
        with pdfium.PdfDocument(path) as pdf:
            citations = extract(client, pdf[page_index], Citations).citations
        for citation in citations:
            print(f"{citation.year:>6} | {citation.title}")


if __name__ == "__main__":
    main()
