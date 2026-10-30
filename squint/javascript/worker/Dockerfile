# syntax=docker/dockerfile:1
# Build from the squint/javascript workspace root

ARG BASE_IMAGE=node:24-trixie-slim

FROM ${BASE_IMAGE} AS base

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    npm_config_store_dir=/pnpm/store

RUN corepack enable && mkdir /app && chown node:node /app

USER node
WORKDIR /app

FROM base AS manifests

# Only the manifests, so source edits don't invalidate the dependency layer
COPY --chown=node:node package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY --chown=node:node worker/package.json worker/
COPY --chown=node:node db/package.json db/

FROM manifests AS deps

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store,uid=1000,gid=1000 \
    pnpm install --frozen-lockfile --filter @squint/worker...

# Restarts the worker when Tilt live updates the source
FROM deps AS dev

COPY --chown=node:node worker worker
COPY --chown=node:node db db

WORKDIR /app/worker

EXPOSE 9090 9229

CMD ["node", "--watch", "--inspect=0.0.0.0:9229", "src/main.ts"]

FROM manifests AS prod-deps

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store,uid=1000,gid=1000 \
    pnpm install --frozen-lockfile --prod --filter @squint/worker

FROM ${BASE_IMAGE}

ENV NODE_ENV=production

USER node
WORKDIR /app/worker

# The workspace keeps the packages in /app/node_modules/.pnpm and links them from worker/node_modules
COPY --from=prod-deps /app/node_modules /app/node_modules
COPY --from=prod-deps /app/worker/node_modules node_modules
COPY --chown=node:node worker/package.json ./
COPY --chown=node:node worker/src src
COPY --chown=node:node db/package.json /app/db/
COPY --chown=node:node db/src /app/db/src

EXPOSE 9090

CMD ["node", "src/main.ts"]
