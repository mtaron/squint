import os
from pathlib import Path

REPOSITORY = Path(__file__).parents[5]

# What the deployment sets, for the models `task download-models` fetches. PyTorch reads the
# allocator setting when it first touches the GPU, which is shared with the dev cluster.
os.environ.setdefault(
    "MODEL_PATH", str(REPOSITORY / "models" / "NeoMME-260M-Retriever")
)
os.environ.setdefault(
    "LOCAL_KERNELS",
    f"kernels-community/flash-attn2={REPOSITORY / 'models' / 'kernels' / 'flash-attn2'}",
)
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
