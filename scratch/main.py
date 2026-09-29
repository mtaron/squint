from pathlib import Path

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
