from pathlib import Path

from huggingface_hub import snapshot_download

DATASETS_DIR = Path(__file__).parent / "datasets"

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
            print(f"Skipping {repo_id}, already downloaded")
            continue
        print(f"Downloading {repo_id} -> {local_dir}")
        snapshot_download(repo_id=repo_id, repo_type="dataset", local_dir=local_dir)
        done_marker.touch()


def main():
    download_datasets()


if __name__ == "__main__":
    main()
