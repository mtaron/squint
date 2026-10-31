# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS build

WORKDIR /src
COPY pyproject.toml uv.lock ./

RUN uv export --frozen --no-emit-project --output-file requirements.txt \
    && uv pip install --target /devtools --compile-bytecode --requirements requirements.txt

COPY debug_worker.py /devtools/

# Only the files, to mount as an image volume on the workers' PYTHONPATH
FROM scratch
COPY --from=build /devtools /
