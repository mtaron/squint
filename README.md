<p align="center">
  <img src="squint/javascript/ui/src/lib/assets/favicon.svg" alt="squint logo" width="96">
</p>

<h1 align="center">
  squint<br>
  <sub><sub><em>A self-hostable, vision-first document processing pipeline</em></sub></sub>
</h1>

[ColPali](https://huggingface.co/blog/manu/colpali) was a paradigm shift in document retrieval. Instead of using a complex retrieval pipeline with OCR, page segmentation, reading order reconstruction, etc., ColPali-style models just embed page images directly. This project is a personal side quest to see how far I can take a "vision-only" document processing pipeline by combining late-interaction page embeddings for search ([NeoMME](https://huggingface.co/blog/Hcompany/neomme) in this case) with a vision-language model ([Qwen3-VL](https://github.com/qwenlm/qwen3-vl)).

The fundamental job squint does is apply a schema across documents with grounding. The late-interaction page embeddings allow it to do so efficiently over a large corpus.

## Principles
- **Efficiency**: Many document-specific problems can be solved with smaller models for a very reasonable accuracy trade-off. You can always throw a bigger model at a problem, but I'm curious how low you can drive cost per page and pages per second while still having acceptable results.
- **Vision-first**: squint should work just as well with scanned PDFs (and any other document type!) as born-digital documents. No docling or PDF parsing, just pixels.
- **Lazy**: Document processing pipelines often do an enormous amount of per-page work that the user will never care about. Delay work until it is really needed.
- **Self-hostable**: Building this way saves money on a cloud GPU during development, enables a streamlined local development flow, and sets you up for BYOC deployment.

## Components
- Embeddings: [NeoMME](https://huggingface.co/blog/Hcompany/neomme)
- VLM: [Qwen3-VL](https://github.com/qwenlm/qwen3-vl)
- Durable worker orchestration: [Temporal](https://docs.temporal.io/)
- Vector store: [Milvus](https://milvus.io/docs)
- Web UI: [SvelteKit](https://svelte.dev/docs/kit/introduction) with remote functions and async enabled
- Key-value database: [Dragonfly](https://www.dragonflydb.io/docs)
- Model hosting: [vLLM](https://docs.vllm.ai/projects/production-stack/en/latest/)
- Networking: [agentgateway](https://agentgateway.dev/docs/kubernetes/latest/)

There are a couple of "dev-only" toy components that I would definitely swap out if I deployed this for real:
- Relational database: [CloudNativePG](https://cloudnative-pg.io/docs/1.30/). This should probably be replaced with Neon.
- Object store: [versitygw](https://github.com/versity/versitygw). This is essentially a stand-in for S3 during development.

## Local development
In addition to exploring a vision-first approach, this project is a playground for exploring developer tooling for microservice development in Kubernetes. This has been a huge pain point for me in the past: fetching a bunch of secrets, port-forwarding a bunch of dependent services, countless VS Code windows to run a subset of services locally, etc. This project uses:
- [kind](https://kind.sigs.k8s.io/) via [nvkind](https://github.com/NVIDIA/nvkind) to create a local Kubernetes cluster with GPU access
- [Tilt](https://docs.tilt.dev/) for live reloading of services in the cluster and port-forwarding a debugger port

Nothing runs outside the cluster. Debugging is always remote debugging to the container in the cluster. mTLS is set up between services in the cluster, but no cert needs to be deployed to the dev machine. I'm pretty happy with how it's working so far.

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

### Dev cluster

```sh
task install-local-certs
task create-dev-cluster
```
