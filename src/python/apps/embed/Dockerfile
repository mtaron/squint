# syntax=docker/dockerfile:1
#
# Build from src/python, since the app depends on ../../packages:
#   docker build --file apps/embed/Dockerfile --tag squint-embed .

ARG CUDA_IMAGE=nvidia/cuda:13.4.2-base-ubuntu26.04

FROM ${CUDA_IMAGE} AS base

RUN apt-get update \
    && apt-get install --yes --no-install-recommends python3.14 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=python3.14 \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY apps/embed /app/apps/embed
COPY packages /app/packages

# The torch cu130 wheels bundle the CUDA runtime libraries, so the base image
# only needs to provide the driver hooks for the NVIDIA container runtime.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project /app/apps/embed --frozen --no-dev --no-editable

FROM base

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/apps/embed /app/apps/embed

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER ubuntu
WORKDIR /app/apps/embed

ENTRYPOINT ["python", "main.py"]
