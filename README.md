# squint
A self-hostable, vision-first document processing pipeline.

## Components
- hosted Neon for the database
- self-hosted Temporal: https://github.com/temporalio/helm-charts
- embeddings: https://huggingface.co/blog/Hcompany/neomme
- self-hosted milvus: https://github.com/milvus-io/milvus
  - https://milvus.io/docs/search-with-embedding-lists.md#ColPali-document-retrieval-system
- test dataset: https://huggingface.co/collections/vidore/vidore-benchmark-v3
## Local development

Development runs on a local [kind](https://kind.sigs.k8s.io/) cluster with GPU access, created with [nvkind](https://github.com/NVIDIA/nvkind).

### Host prerequisites

Install these using your distribution's instructions:

- An NVIDIA driver. `nvidia-smi -L` should list your GPU.
- [Docker](https://docs.docker.com/engine/install/)
- The [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

Then configure Docker to use the toolkit (one time):

```sh
sudo nvidia-ctk runtime configure --runtime=docker --set-as-default --cdi.enabled
sudo nvidia-ctk config --set accept-nvidia-visible-devices-as-volume-mounts=true --in-place
sudo systemctl restart docker
```

### Tools

[mise](https://mise.jdx.dev/) installs everything else needed for development.

```sh
mise install --locked
```
