# syntax=docker/dockerfile:1

ARG BASE_IMAGE=ubuntu:26.04

FROM ${BASE_IMAGE} AS base

ARG EXTRA_PACKAGES=""

RUN apt-get update \
    && apt-get install --yes --no-install-recommends python3.14 ${EXTRA_PACKAGES} \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

ARG APP

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=python3.14 \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Only the project metadata, so source edits don't invalidate the dependency layer
COPY apps/${APP}/pyproject.toml apps/${APP}/uv.lock /app/apps/${APP}/
COPY packages /app/packages

FROM builder AS venv-release

ARG APP

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project /app/apps/${APP} --frozen --no-dev --no-editable

FROM builder AS venv-debug

ARG APP

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project /app/apps/${APP} --frozen --no-dev --group debug

FROM base AS runtime

ARG APP

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1

USER ubuntu
WORKDIR /app/apps/${APP}

ENTRYPOINT ["python", "main.py"]

FROM runtime AS debug

ARG APP

COPY --from=venv-debug /opt/venv /opt/venv
COPY --chown=ubuntu:ubuntu packages /app/packages
COPY --chown=ubuntu:ubuntu apps/${APP} /app/apps/${APP}

FROM runtime AS release

ARG APP

COPY --from=venv-release /opt/venv /opt/venv
COPY apps/${APP} /app/apps/${APP}
