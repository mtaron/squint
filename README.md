# squint
A self-hostable, vision-first document processing pipeline.

## Components
- self-hosted Temporal: https://github.com/temporalio/helm-charts
- embeddings: https://huggingface.co/blog/Hcompany/neomme
- self-hosted milvus: https://github.com/milvus-io/milvus
  - https://milvus.io/docs/search-with-embedding-lists.md#ColPali-document-retrieval-system

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

### Cluster

```sh
task create-dev-cluster
task deploy
```

The cluster mounts this repository's `squint/` folder into its nodes, and in development each app's Deployment runs from that mounted source under [debugpy](https://github.com/microsoft/debugpy). Apps reach cluster services by their in-cluster names; nothing is exposed to the host.

To debug an app, pick its `(kind)` configuration in VS Code and press F5. That restarts the pod and attaches the debugger. The pod waits at startup until the debugger attaches. Code changes only need another F5. The dev image (`squint/Dockerfile.dev`) contains just the dependencies, so `task image APP=<app>` rebuilds it only when a `pyproject.toml` or `uv.lock` changes.

