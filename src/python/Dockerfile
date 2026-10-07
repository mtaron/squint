# syntax=docker/dockerfile:1
#
# Build from src/python, since the apps depend on ../../packages:
#   docker build --build-arg APP=<app> --tag registry.localhost/squint-<app>:test .
#
# APP is a directory name under apps/. GPU apps (embed) need a CUDA base:
#   docker build --build-arg APP=embed \
#       --build-arg BASE_IMAGE=nvidia/cuda:13.4.2-base-ubuntu26.04 \
#       --tag registry.localhost/squint-embed:test .

ARG BASE_IMAGE=ubuntu:26.04

FROM ${BASE_IMAGE} AS base

RUN apt-get update \
    && apt-get install --yes --no-install-recommends python3.14 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

ARG APP

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=python3.14 \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY apps/${APP} /app/apps/${APP}
COPY packages /app/packages

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project /app/apps/${APP} --frozen --no-dev --no-editable

FROM base

ARG APP

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/apps/${APP} /app/apps/${APP}

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER ubuntu
WORKDIR /app/apps/${APP}

ENTRYPOINT ["python", "main.py"]
