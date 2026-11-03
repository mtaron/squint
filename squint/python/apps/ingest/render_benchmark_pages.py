"""Renders a ViDoRe v3 dataset's PDFs the way ingest does, along with its English queries, for
`task search-bench`. Each page is saved with its content box, which the embed worker crops to."""

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pypdfium2 as pdfium
from pyarrow import parquet  # ty: ignore[unresolved-import]

from rasterize import rasterize_page

QUERY_LANGUAGE = "english"


def render_document(pdf: Path, output: Path) -> dict[int, list[int] | None]:
    """Page numbers start at 1, as they do in ingest."""
    pages = output / pdf.stem
    pages.mkdir(parents=True, exist_ok=True)
    content_boxes = {}
    document = pdfium.PdfDocument(pdf)
    for index, page in enumerate(document, start=1):
        rasterized = rasterize_page(page)
        (pages / f"{index}.jpg").write_bytes(rasterized.image)
        content_boxes[index] = rasterized.content_box
    return content_boxes


def english_queries(dataset: Path) -> list[str]:
    rows = []
    for path in sorted((dataset / "queries").glob("*.parquet")):
        rows += parquet.read_table(path, columns=["query", "language"]).to_pylist()
    return [row["query"] for row in rows if row["language"] == QUERY_LANGUAGE]


def run(dataset: Path, output: Path) -> None:
    pdfs = sorted((dataset / "pdfs").glob("*.pdf"))
    with ProcessPoolExecutor() as executor:
        boxes = executor.map(render_document, pdfs, [output / "pages"] * len(pdfs))
        content_boxes = dict(zip((pdf.stem for pdf in pdfs), boxes, strict=True))
    (output / "content_boxes.json").write_text(json.dumps(content_boxes))
    (output / "queries.json").write_text(json.dumps(english_queries(dataset)))
    pages = sum(len(document) for document in content_boxes.values())
    print(f"rendered {pages} pages of {len(pdfs)} documents into {output}")


if __name__ == "__main__":
    run(Path(sys.argv[1]), Path(sys.argv[2]))
