from collections import defaultdict
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import fmean, median

import pypdfium2 as pdfium
from huggingface_hub import snapshot_download
from lightkube import Client
from lightkube.resources.core_v1 import Service
from pymilvus import MilvusClient
from typing import Any, Literal

import requests
import torch
from PIL import Image
from sentence_transformers.util import cos_sim, mean_maxsim

from transformers import BatchFeature, NeoMMEForRetrieval, NeoMMEProcessor

DATASETS_DIR = Path(__file__).parent / "datasets"
MILVUS_PORT = 19530

# Longest-side cap the NeoMME processor applies (processor_config.json `max_side`).
MAX_SIDE_LENGTH = 2048
# Grayscale values below this count as ink when finding the content bounds.
INK_THRESHOLD = 250
# Pages with little content (a lone page number, a short last line) would otherwise be
# blown up far past the text sizes the model trained on.
MAX_DPI = 300
# A content crop keeping less than this share of the CropBox area counts as smaller
# (the probe's one-pixel padding keeps full-bleed pages just under 100%).
SMALLER_THRESHOLD = 0.99

DATASETS = [
    "vidore/vidore_v3_hr",
    "vidore/vidore_v3_finance_en",
    "vidore/vidore_v3_industrial",
    "vidore/vidore_v3_pharmaceuticals",
    "vidore/vidore_v3_computer_science",
    "vidore/vidore_v3_energy",
    "vidore/vidore_v3_physics",
    "vidore/vidore_v3_finance_fr",
    "allenai/olmOCR-bench",
]


def download_datasets():
    for repo_id in DATASETS:
        local_dir = DATASETS_DIR / repo_id.split("/")[-1]
        done_marker = local_dir / ".complete"
        if done_marker.exists():
            continue

        print(f"Downloading {repo_id} -> {local_dir}")
        snapshot_download(repo_id=repo_id, repo_type="dataset", local_dir=local_dir)
        done_marker.touch()


def content_crop(page: pdfium.PdfPage, max_side_length: int) -> tuple[float, ...]:
    """(left, bottom, right, top) margins around the page's ink, in PDF canvas units.

    PDFs rarely set an ArtBox (pypdfium2 falls back to the CropBox), so find the
    ink bounds from a low-resolution grayscale render instead.
    """

    # Use a quarter of the max size length for the probe render
    max_side_length=max_side_length // 4

    width, height = page.get_width(), page.get_height()
    scale = max_side_length / max(width, height)
    probe = page.render(scale=scale, grayscale=True).to_pil()
    bbox = probe.point(lambda v: 255 if v < INK_THRESHOLD else 0).getbbox()
    if bbox is None:  # blank page
        return (0, 0, 0, 0)

    # Pad by a probe pixel so faint anti-aliased edges aren't clipped.
    left, top, right, bottom = (bbox[0] - 1, bbox[1] - 1, bbox[2] + 1, bbox[3] + 1)
    return (
        max(0, left / scale),
        max(0, height - bottom / scale),
        max(0, width - right / scale),
        max(0, top / scale),
    )


def render_scale(
    page: pdfium.PdfPage, crop: tuple[float, ...], max_side_length: int
) -> float:
    """Scale that renders the cropped page with its longest side at max_side_length
    pixels, capped at MAX_DPI."""
    left, bottom, right, top = crop
    long_side = max(page.get_width() - left - right, page.get_height() - bottom - top)
    # render() rounds the page size and each crop edge up; a pixel of slack keeps the
    # result within max_side (it lands 1-2px under, which pads to the same patch grid).
    return min((max_side_length - 1) / long_side, MAX_DPI / 72)


def rasterize_pdf(path: Path, max_side_length: int = MAX_SIDE_LENGTH) -> Iterator[Image.Image]:
    """Render each page cropped to its content, with the longest side at max_side pixels."""
    pdf = pdfium.PdfDocument(path)
    try:
        pdf.init_forms()  # render filled-in form fields
        for page in pdf:
            crop = content_crop(page, max_side_length)
            scale = render_scale(page, crop, max_side_length)
            yield page.render(scale=scale, crop=crop, rev_byteorder=True).to_pil()
    finally:
        pdf.close()

def gateway_address() -> str | None:
    """Load balancer address of the gateway proxy, or None if not assigned yet."""
    svc = Client().get(Service, "agentgateway-proxy", namespace="squint")
    ingress = svc.status.loadBalancer.ingress
    if not ingress:
        return None
    return ingress[0].hostname or ingress[0].ip


def check_milvus():
    address = gateway_address()
    if address is None:
        print("Gateway has no load balancer address; run `task lb-dev-cluster`")
        return
    uri = f"http://{address}:{MILVUS_PORT}"
    client = MilvusClient(uri=uri)
    print(f"Connected to {uri}, server version {client.get_server_version()}")
    print(f"Databases: {client.list_databases()}")
    print(f"Collections: {client.list_collections()}")


def model_test():
    model_name = "Hcompany/NeoMME-800M-Retriever"
    processor = NeoMMEProcessor.from_pretrained(model_name)
    model = NeoMMEForRetrieval.from_pretrained(model_name, device_map="auto")

    def encode(
        messages: list[list[dict[str, Any]]],
        task: Literal["query", "document"],
    ) -> BatchFeature:
        return processor.apply_chat_template(
            messages,
            task=task,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            processor_kwargs={"padding": "longest"},
        )

    # Document images (our corpus)
    image_urls = [
        "https://github.com/tonywu71/colpali-cookbooks/blob/6ef1332da6bcb48c7ef1f19b25bfa555be7031a8/examples/data/shift_kazakhstan.jpg?raw=true",
        "https://github.com/tonywu71/colpali-cookbooks/blob/6ef1332da6bcb48c7ef1f19b25bfa555be7031a8/examples/data/energy_electricity_generation.jpg?raw=true",
    ]
    documents = [Image.open(requests.get(url, stream=True).raw) for url in image_urls]

    # Queries
    queries = [
        "Quelle partie de la production pétrolière du Kazakhstan provient de champs en mer ?",
        "Which hour of the day had the highest overall electricity generation in 2019?",
    ]

    document_messages = [
        [{"role": "user", "content": [{"type": "image", "image": document}]}]
        for document in documents
    ]
    query_messages = [[{"role": "user", "content": query}] for query in queries]

    inputs_documents = encode(document_messages, "document").to(model.device)
    inputs_text = encode(query_messages, "query").to(model.device)

    with torch.inference_mode():
        document_outputs = model(**inputs_documents)
        query_outputs = model(**inputs_text)

    late_scores = mean_maxsim(
        query_outputs.embeddings,
        document_outputs.embeddings,
        a_mask=inputs_text["attention_mask"],
        b_mask=inputs_documents["attention_mask"],
    )
    dense_scores = cos_sim(
        query_outputs.dense_embeddings, document_outputs.dense_embeddings
    )

    # Expected: late_scores[0, 0] > late_scores[0, 1] and late_scores[1, 1] > late_scores[1, 0].
    print(late_scores, dense_scores)


def main():
    check_milvus()
    download_datasets()
    model_test()


if __name__ == "__main__":
    main()
